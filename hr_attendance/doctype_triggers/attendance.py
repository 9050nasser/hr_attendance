import frappe
from frappe import _
from frappe.utils import get_weekday, get_datetime, nowdate, get_time, get_first_day, get_last_day, add_days
from datetime import datetime, timedelta
from hrms.hr.doctype.leave_application.leave_application import get_leave_balance_on


def on_submit(doc, method):
    attendance_rule_name, holiday_list = frappe.db.get_value("Employee", doc.employee, ["custom_attendance_rule", "holiday_list"])
    if attendance_rule_name:
        attendance_rule = frappe.get_doc("Attendance Rule", attendance_rule_name)
        check_for_absence(doc, attendance_rule, holiday_list)
        check_for_late_early(doc, attendance_rule)
        check_for_overtime(doc, attendance_rule)

def on_cancel(doc, method):
    leave = frappe.db.get_value("Leave Ledger Entry", [["transaction_name", "=", doc.name]])
    if leave:
        frappe.db.set_value("Leave Ledger Entry", leave, "docstatus", 2)
        frappe.delete_doc("Leave Ledger Entry", leave, force=1, ignore_permissions=True)

def check_for_absence(doc, attendance_rule, holiday_list):
    if doc.status == "Absent":
        if attendance_rule.enable_absence_rule:
            if attendance_rule.deduct_from_leave_balance:
                leave_allocation_name = frappe.db.get_value("Leave Allocation", [
                    ["from_date", "<=", doc.attendance_date],
                    ["employee", "=", doc.employee],
                    ["docstatus", "=", 1],
                    ["to_date", ">=", doc.attendance_date],
                    ["leave_type", "=", attendance_rule.leave_type]
                ]
                , order_by="creation DESC")
                if not leave_allocation_name:
                    frappe.msgprint(_("There is no leave allocation linked with employee {0} with leave type {1}".format(doc.employee, attendance_rule.leave_type)))
                if get_leave_balance_on(doc.employee, attendance_rule.leave_type, date= nowdate()) == 0:
                    frappe.msgprint(_("Employee {0} balance of {1} is Zero").format(doc.employee, attendance_rule.leave_type))
                else:
                    leave = frappe.get_doc(dict(
                        doctype = "Leave Ledger Entry",
                        employee = doc.employee,
                        leave_type = attendance_rule.leave_type,
                        transaction_type = "Leave Application",
                        transaction_name = doc.name,
                        company = doc.company,
                        leaves = abs(attendance_rule.leave_deduction_absent_factor) * -1,
                        from_date = doc.attendance_date,
                        to_date = add_days(doc.attendance_date, attendance_rule.leave_deduction_absent_factor - 1),
                        holiday_list = holiday_list
                    ))
                    leave.insert(ignore_permissions=True, ignore_links=True)
                    leave.submit()
            if attendance_rule.deduct_from_salary:
                base = get_base(doc.employee)
                make_employee_penalty(
                    doc.employee, 
                    doc.attendance_date, 
                    "Days",
                    "Absence",
                    doc.name,
                    base*attendance_rule.salary_deduction_absent_factor/30,
                    days=attendance_rule.salary_deduction_absent_factor
                )

def check_for_late_early(doc, attendance_rule):
    if not doc.shift:
        frappe.throw(_("Shift is not specified"))
    else:
    
        (shift_start,
        shift_end,
        enable_late_entry_marking,
        enable_early_exit_marking,
        late_entry_grace_period,
        early_exit_grace_period) = frappe.db.get_value("Shift Type", doc.shift,
            ["start_time",
            "end_time",
            "enable_late_entry_marking",
            "enable_early_exit_marking",
            "late_entry_grace_period",
            "early_exit_grace_period"]
        )
        duration = (shift_end.total_seconds() - shift_start.total_seconds())/3600
        
        if attendance_rule.enable_late_rule or attendance_rule.enable_late_penalty:
            mark_late_in(
                doc,
                attendance_rule,
                enable_late_entry_marking,
                late_entry_grace_period,
                shift_start,
                duration
            )
        if attendance_rule.enable_early_out_rule or attendance_rule.enable_early_out_penalty:
            mark_early_out(
                doc,
                attendance_rule,
                enable_early_exit_marking,
                early_exit_grace_period,
                shift_end,
                duration
            )

def make_employee_penalty(
    employee,
    date,
    Type,
    reason,
    attendance,
    penalty_amount,
    days=0,
    amount=0):

    ep = frappe.get_doc(dict(
        doctype = "Employee Penalty",
        penalty_date = date,
        penalty_type = Type,
        days= days,
        reason=reason,
        amount=amount,
        attendance = attendance,
        employee = employee,
        penalty_amount = penalty_amount
    ))
    ep.insert()
    return ep 

def get_factor(factors, minutes, factor_str = "factor_per_minute"):
    factor = 0
    for row in factors:
        factor = getattr(row, factor_str, 0)
        if minutes < row.to_min:
            return factor
    return factor

def get_base(employee):
    base = frappe.db.get_value("Salary Structure Assignment", [["employee", "=", employee], ["docstatus", "=", 1]], "base", order_by="creation DESC")
    if not base:
        frappe.throw(_("Please specify Salary Structure Assignment for employee {0}".format(employee)))
    return base

def convert_to_datetime(time):
    try:
        return datetime.strptime(str(time.time()), "%H:%M:%S")
    except Exception as e:
        return datetime.strptime(str(time.time()), "%H:%M:%S.%f")

def mark_late_in(
    doc,
    attendance_rule,
    enable_late_entry_marking,
    late_entry_grace_period,
    shift_start,
    duration):

    if doc.status != "Absent":
        if enable_late_entry_marking:
            shift_start_time = convert_to_datetime(datetime.min + shift_start)
            attendance_in_time = convert_to_datetime(get_datetime(doc.in_time))
            total_in_difference = (attendance_in_time - shift_start_time).total_seconds()/60


            if total_in_difference > late_entry_grace_period:
                if attendance_rule.enable_late_penalty: 
                    factor = get_factor(attendance_rule.late_penalty_table, total_in_difference, "factor_in_days")
                else:
                    factor = get_factor(attendance_rule.late_rule_table, total_in_difference)
                base = get_base(doc.employee)
                salary_portion = base / 30 if attendance_rule.enable_late_penalty else base / 30 / duration / 60
                if attendance_rule.enable_late_penalty:
                    total_in_difference = 1
                amount = total_in_difference * factor * salary_portion
                make_employee_penalty(
                    doc.employee,
                    doc.attendance_date,
                    "Amount",
                    "Late In",
                    doc.name,
                    amount,
                    amount = amount
                )

def mark_early_out(
    doc,
    attendance_rule,
    enable_early_exit_marking,
    early_exit_grace_period,
    shift_end,
    duration):
    if doc.status != "Absent":
        if enable_early_exit_marking:
            shift_end_time = convert_to_datetime(datetime.min + shift_end)
            attendance_out_time = convert_to_datetime(get_datetime(doc.out_time))
            total_out_difference = (shift_end_time - attendance_out_time).total_seconds()/60

            if total_out_difference > early_exit_grace_period:
                if attendance_rule.enable_early_out_penalty:
                    factor = get_factor(attendance_rule.early_out_penalty, total_out_difference, "factor_per_days")
                else:
                    factor = get_factor(attendance_rule.early_out_rule, total_out_difference)
                base = get_base(doc.employee)
                salary_portion = base / 30 if attendance_rule.enable_early_out_penalty else base / 30 / (duration*60)
                if attendance_rule.enable_early_out_penalty:
                    total_out_difference = 1
                amount = total_out_difference * factor * salary_portion
                make_employee_penalty(
                    doc.employee,
                    doc.attendance_date,
                    "Amount",
                    "Early Out",
                    doc.name,
                    amount,
                    amount = amount
                )

def check_for_overtime(doc, attendance_rule):
    if (
        attendance_rule.enable_overtime or
        attendance_rule.enable_overtime_morningevening or
        attendance_rule.enable_overtime_categories or
        attendance_rule.enable_overtime_fixed_amount
        ):
        max_month, max_day, mintime = (
            attendance_rule.overtime_maximum_per_month_hours,
            attendance_rule.overtime_maximum_per_day_hours,
            attendance_rule.maximum_early_overtime_minutes
        )
        shift_start, shift_end = frappe.db.get_value("Shift Type", doc.shift, ["start_time", "end_time"])
        overtime_type = get_overtime_type(doc.employee, doc.attendance_date)

        mark_early_overtime(
            doc,
            attendance_rule,
            max_month,
            max_day,
            mintime,
            shift_start,
            overtime_type
        )
        if overtime_type == "Normal Overtime":
            mark_out_overtime(
                doc,
                attendance_rule,
                max_month,
                max_day,
                shift_end
            )

def mark_early_overtime(doc, attendance_rule, max_month, max_day, mintime, shift_start, overtime_type):
    if doc.status != "Absent":
        exceed = False
        if overtime_type == "Normal Overtime":
            in_time = convert_to_datetime(get_datetime(doc.in_time))
            shift_start = convert_to_datetime(datetime.min + shift_start)
            diff = (shift_start - in_time).total_seconds()/3600
            overtime_end_time = shift_start
        else:
            diff = (get_datetime(doc.out_time) - get_datetime(doc.in_time)).total_seconds()/3600
            overtime_end_time = get_time(get_datetime(doc.out_time))

        if max_day != 0 and check_exceed_maximum(doc.attendance_date, max_day, doc.employee, diff, "d"):
            total_overtime = get_exceed_maximum(doc.attendance_date, max_day, doc.employee, diff, "d")
            diff = max_day - total_overtime
            exceed = True

        if max_month != 0 and check_exceed_maximum(doc.attendance_date, max_month, doc.employee, diff, "m"):
            total_overtime = get_exceed_maximum(doc.attendance_date, max_month, doc.employee, diff, "m")
            diff = max_month - total_overtime
            exceed = True
            
        if diff > mintime/60 or exceed:
            base = get_base(doc.employee)
            if diff > 0:
                amount ,factor = get_overtime(diff, attendance_rule, overtime_type, base, doc.in_time, doc.out_time, doc.shift)
                overtime_name = check_overtime_exist(doc.employee,doc.attendance_date,
                    get_time(get_datetime(doc.in_time)), overtime_end_time, overtime_type)
                early_in = 0
                if overtime_type == "Normal Overtime":
                    early_in = 1
                if not overtime_name:
                    make_overtime_request(
                        doc.employee,
                        doc.attendance_date,
                        get_time(get_datetime(doc.in_time)),
                        overtime_end_time,
                        overtime_type,
                        factor,
                        amount,
                        diff,
                        early_in = early_in,
                        attendance = doc.name
                    )

def mark_out_overtime(doc, attendance_rule, max_month, max_day, shift_end):
    if doc.status != "Absent":
        out_time = convert_to_datetime(get_datetime(doc.out_time))
        shift_end = convert_to_datetime(datetime.min + shift_end)
        diff = (out_time - shift_end).total_seconds()/3600

        base = get_base(doc.employee)
        if max_day != 0 and check_exceed_maximum(doc.attendance_date, max_day, doc.employee, diff, "d"):
            total_overtime = get_exceed_maximum(doc.attendance_date, max_day, doc.employee, diff, "d")
            diff = max_day - total_overtime

        if max_month != 0 and check_exceed_maximum(doc.attendance_date, max_month, doc.employee, diff, "m"):
            total_overtime = get_exceed_maximum(doc.attendance_date, max_month, doc.employee, diff, "m")
            diff = max_month - total_overtime

        if diff > 0:
            amount ,factor = get_overtime(
                diff,
                attendance_rule,
                "Normal Overtime",
                base,
                get_datetime(doc.in_time),
                get_datetime(doc.out_time), 
                shift = doc.shift,
                morning = False
            )
            overtime_name = check_overtime_exist(
                doc.employee,
                doc.attendance_date,
                shift_end,
                get_time(doc.out_time),
                "Normal Overtime"
            )
            if not overtime_name:
                make_overtime_request(
                    doc.employee,
                    doc.attendance_date,
                    shift_end,
                    get_time(doc.out_time),
                    "Normal Overtime",
                    factor,
                    amount,
                    diff,
                    attendance = doc.name
                )

def check_overtime_exist(
    employee,
    date,
    overtime_start,
    overtime_end,
    overtime_type,
):
    return frappe.db.get_value("Overtime Request", {
        "date" : date,
        "employee" : employee,
        "overtime_start_time" : overtime_start,
        "overtime_end_time" : overtime_end,
        "overtime_type" : overtime_type,
    })

def make_overtime_request(
    employee,
    date,
    overtime_start,
    overtime_end,
    overtime_type,
    overtime_factor,
    overtime_amount,
    total_hours,
    early_in = 0,
    attendance = ""
):
    overtime = frappe.get_doc(dict(
        date = date,
        employee = employee,
        overtime_start_time = overtime_start,
        overtime_end_time = overtime_end,
        overtime_type = overtime_type,
        calculated_overtime_factor = overtime_factor,
        calculated_overtime_amount = overtime_amount,
        total_overtime_hours = total_hours,
        doctype = "Overtime Request",
        early_in = early_in, 
        attendance = attendance
    ))
    overtime.insert()
    return overtime

def check_exceed_maximum(attendance_date, max, employee, current_hours, Type):
    if Type == "m":
        date_range = [get_first_day(attendance_date), get_last_day(attendance_date)]
    else:
        date_range = [attendance_date, attendance_date]
    overtime = frappe.db.get_value("Overtime Request", 
    [
        ["employee", "=", employee],
        ["date", "between", date_range],
        ["docstatus", "=", 1],
    ],
    "sum(total_overtime_hours)")
    overtime = overtime if overtime else 0
    if (overtime + current_hours) > max:
        return True
    return

def get_exceed_maximum(attendance_date, max, employee, current_hours, Type):
    if Type == "m":
        date_range = [get_first_day(attendance_date), get_last_day(attendance_date)]
    else:
        date_range = [attendance_date, attendance_date]
    overtime = frappe.db.get_value("Overtime Request", 
    [
        ["employee", "=", employee],
        ["date", "between", date_range],
        ["docstatus", "=", 1],
    ],
    "sum(total_overtime_hours)")
    overtime = overtime if overtime else 0
    if (overtime + current_hours) > max:
        return overtime
    return

def get_overtime_type(employee, attendance_date, overtime_type = ""):
    holiday_list_name = frappe.db.get_value("Employee", employee, "holiday_list")
    if not holiday_list_name:
        frappe.throw(_("Holiday List is not specified for employee {0}").format(employee))
    if frappe.db.get_value("Holiday", {"parent":holiday_list_name, "holiday_date":attendance_date, "weekly_off":1}):
        return "Weekend Overtime"
    elif frappe.db.get_value("Holiday", {"parent":holiday_list_name, "holiday_date":attendance_date, "weekly_off":0}):
        return "Holiday Overtime"
    else:
        return "Normal Overtime"

def get_overtime(
    diff,
    attendance_rule,
    overtime_type,
    base,
    in_time = "",
    out_time="",
    shift="",
    morning = True
):
    shift_start, shift_end = frappe.db.get_value("Shift Type", shift, ["start_time", "end_time"])
    shift_duration = (shift_end.total_seconds() - shift_start.total_seconds())/3600
    factor = 1
    overtime = 0
    hourly_salary = base / 30 / shift_duration
    
    if attendance_rule.enable_overtime_fixed_amount:
        factor = attendance_rule.fixed_amount_per_hour
        overtime = diff * factor
    elif attendance_rule.enable_overtime_categories:
        last_overtime_period = 0
        for row in attendance_rule.overtime_category:

            if diff*60 < row.to_min:
                overtime += (diff*60 - row.from_min +1) * row.factor_per_minute * hourly_salary / 60
                factor = row.factor_per_minute
                last_overtime_period = 0
                break
            else:
                overtime += (row.to_min - row.from_min +1) * row.factor_per_minute * hourly_salary / 60
                last_overtime_period = row.to_min
            factor = row.factor_per_minute
        if last_overtime_period:
            overtime += (diff*60 - last_overtime_period) * factor * hourly_salary / 60
    elif attendance_rule.enable_overtime_morningevening:
        if overtime_type == "Normal Overtime":
            if morning:
                mstart, mend = convert_to_datetime(in_time), convert_to_datetime(datetime.min + shift_start)
            elif (convert_to_datetime(out_time)-convert_to_datetime(in_time)).total_seconds() > diff*3600:
                mstart, mend = convert_to_datetime(datetime.min + shift_end), convert_to_datetime(datetime.min + shift_end + timedelta(seconds=diff*3600))
            else:
                mstart, mend = convert_to_datetime(datetime.min + shift_end), convert_to_datetime(out_time)
        else:
            if (convert_to_datetime(out_time)-convert_to_datetime(in_time)).total_seconds() > diff*3600:
                start_time = datetime.min + attendance_rule.morning_overtime_start_time
                mstart, mend = convert_to_datetime(start_time), convert_to_datetime(start_time + timedelta(seconds=diff*3600))
            else:
                mstart, mend = convert_to_datetime(in_time), convert_to_datetime(out_time)

        for row in get_diff_factor_for_morningevening(attendance_rule, mstart, mend, overtime_type):
            overtime += row['diff'] * row['factor'] * hourly_salary
            factor = row['factor']
    elif attendance_rule.enable_overtime:
        if overtime_type == "Weekend Overtime":
            factor = attendance_rule.overtime_weekend_factor_per_hour
        elif overtime_type == "Holiday Overtime":
            factor = attendance_rule.overtime_holiday_factor_per_hour
        elif overtime_type == "Normal Overtime":
            factor = attendance_rule.overtime_normal_factor_per_hour
        overtime = diff * factor * hourly_salary
    return (overtime, factor)

def get_diff_factor_for_morningevening(attendance_rule, in_time:datetime, out_time:datetime, overtime_type):
    diffs_and_factors = []
    m_overtime_start = convert_to_datetime(datetime.min + attendance_rule.morning_overtime_start_time)

    if  (m_overtime_start - convert_to_datetime(in_time)).total_seconds() > 0:
        start_time = m_overtime_start
    else:
        start_time = convert_to_datetime(in_time)

    m_overtime_end = convert_to_datetime(datetime.min + attendance_rule.morning_overtime_end_time)
    if (convert_to_datetime(out_time) - m_overtime_end).total_seconds() > 0:
        end_time = m_overtime_end
    else:
        end_time = convert_to_datetime(out_time)
    if ((end_time - start_time).total_seconds() > 0):
        diffs_and_factors.append(dict(
            diff = (end_time - start_time).total_seconds() / 3600,
            factor = attendance_rule.morning_overtime_factor_per_hour
        ))

    e_overtime_start = convert_to_datetime(datetime.min + attendance_rule.evening_overtime_start_time)
    if (out_time - e_overtime_start).total_seconds() < 0 :
        return diffs_and_factors
    else:
        if  (convert_to_datetime(in_time) - e_overtime_start).total_seconds() > 0:
            start_time = convert_to_datetime(in_time)
        else:
            start_time = e_overtime_start
        e_overtime_end = convert_to_datetime(datetime.min + attendance_rule.evening_overtime_end_time)
        if (convert_to_datetime(out_time) - e_overtime_end).total_seconds() > 0:
            end_time = e_overtime_end
        else:
            end_time = convert_to_datetime(out_time)
        if (end_time - start_time).total_seconds() > 0:    
            diffs_and_factors.append(dict(
                diff = (end_time - start_time).total_seconds()/3600,
                factor = attendance_rule.evening_overtime_factor_per_hour
            ))
    return diffs_and_factors

