import frappe
from frappe import _
from frappe.utils import nowdate, date_diff, get_first_day, get_last_day

def validate(doc, method):

    notification = frappe.get_doc({
        "doctype": "Notification Log",
        "subject":f"Leave Application {doc.name} for employee {doc.employee} has been submitted for your approval.",
        "for_user": doc.leave_approver,
        "type": "Alert",
        "message": f"Leave Application {doc.name} for employee {doc.employee} has been submitted for your approval.",
        "document_type": doc.doctype,
        "document_name": doc.name,
        "read": 0  # Mark notification as unread by default
    })

    notification.insert(ignore_permissions=True)
    frappe.db.commit()
    (
        custom_notice_period_for_annual_leave,
        custom_haj_leave,
        custom_minimum_service_period_for_hag,
        allow_negative
    ) = frappe.db.get_value("Leave Type", doc.leave_type, [
        "custom_notice_period_for_annual_leave",
        "custom_haj_leave",
        "custom_minimum_service_period_for_hag",
        "allow_negative"
    ])
    if not doc.custom_is_an_exception:
        check_for_number_of_applications_exceed(doc.leave_type, doc.employee)
        check_for_number_of_applications_exceed_per_month(doc.leave_type, doc.employee, get_first_day(doc.from_date), get_last_day(doc.from_date))
        validate_application_duration(doc.leave_type, doc.employee, get_first_day(doc.from_date), get_last_day(doc.from_date))
        holiday_list_name = frappe.db.get_value("Employee", doc.employee, "holiday_list")
        if custom_notice_period_for_annual_leave:
            number_of_holidays = frappe.db.count("Holiday", [["parent", "=", holiday_list_name], ["holiday_date","between", [nowdate(), doc.from_date]]])
            number_of_days = date_diff(doc.from_date, nowdate())
            if (number_of_days - number_of_holidays) < custom_notice_period_for_annual_leave + 1:
                frappe.throw(_("Leave applications for {0} must be submitted at least {1:.0f} working days before the leave start date. Please adjust your request.").format(doc.leave_type, custom_notice_period_for_annual_leave))

        # add validation for hag leave (to be in service at least #number of years)
        if custom_haj_leave:
            date_of_joining = frappe.db.get_value("Employee", doc.employee, "date_of_joining")
            if date_diff(doc.from_date, date_of_joining) < custom_minimum_service_period_for_hag * 365:
                frappe.throw(_("Haj Leave can only be applied for after completing {0:.0f} years of service with the company.").format(custom_minimum_service_period_for_hag))
        # display warning for skipped allocations
        if allow_negative:
            frappe.msgprint(_("Leave allocation not required for {0}. Submission allowed.").format(doc.leave_type))

        
def check_for_number_of_applications_exceed(leave_type, employee):
    app_limit = frappe.db.get_value("Leave Type", leave_type, "custom_restrict_allowed_applications_to")
    if app_limit:
        num_of_application = frappe.db.count("Leave Application", {"employee": employee, "leave_type": leave_type, "docstatus": 1, "status": "Approved"})
        if num_of_application >= app_limit:
            frappe.throw(_("You only allowed to create {0:.0f} applications for leave type {1}").format(app_limit, leave_type))

def check_for_number_of_applications_exceed_per_month(leave_type, employee, month_start, month_end):
    app_limit = frappe.db.get_value("Leave Type", leave_type, "custom_allowed_number_of_applications_per_month")
    if app_limit:
        num_of_application = frappe.db.count("Leave Application", {"employee": employee, "leave_type": leave_type, "status": "Approved", "docstatus": 1, "from_date": ["Between", [month_start, month_end]], "to_date": ["Between", [month_start, month_end]]})

        if num_of_application >= app_limit:
            frappe.throw(_("You only allowed to create {0:.0f} applications for leave type {1} per month").format(app_limit, leave_type))

def validate_application_duration(leave_type, employee, month_start, month_end):
    app_limit = frappe.db.get_value("Leave Type", leave_type, "custom_days_allowed_monthly")
    if app_limit:
        num_of_days = frappe.db.get_value("Leave Application", {"employee": employee, "leave_type": leave_type, "status": "Approved", "docstatus": 1, "from_date": ["Between", [month_start, month_end]], "to_date": ["Between", [month_start, month_end]]}, "SUM(total_leave_days) as total_leaves")

        if num_of_days >= app_limit:
            frappe.throw(_("You exceeded the monthly allowed number of days for leave type {0}").format(leave_type))

@frappe.whitelist()
def get_skipped_allocation_leaves():
    return frappe.db.get_list("Leave Type", {"custom_skip_allocation": 1})