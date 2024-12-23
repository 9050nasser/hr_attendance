import frappe
from frappe import _

def on_submit(doc, method):
    frappe.db.set_value("Attendance", doc.custom_worked_on_holiday,{"custom_holiday_worked": 1, "working_hours": 0, "custom_remark":_("Compensatory Leave Applied for Working on Holiday")})

def on_cancel(doc, method):
    frappe.db.set_value("Attendance", doc.custom_worked_on_holiday, {"custom_holiday_worked": 0, "custom_remark":_("Compensatory Leave Cancelled for Working on Holiday")})

def validate(doc, method):
    # check for checkins
    intime, outtime = frappe.db.get_value("Attendance", doc.custom_worked_on_holiday, ["in_time", "out_time"])
    if not (intime or outtime):
        frappe.throw(
            _("No Attendance check-ins found for Employee {0} between {1} and {2}.")
            .format(doc.employee, doc.work_from_date, doc.work_end_date)
        )
    # check for duplicate leave request
    period = [doc.work_from_date, doc.work_end_date]
    exist = frappe.db.get_value(doc.doctype, [["name", "!=", doc.name],["docstatus", "=", 1], ["work_from_date", "between", period], ["work_end_date", "between", period]])
    if exist:
        frappe.throw(_("A compensatory leave request already exists for the same period."))
    
@frappe.whitelist()
def get_attendance_name(employee, attendance_date):
    return frappe.db.get_value("Attendance", {"employee": employee, "attendance_date": attendance_date, "docstatus": 1})