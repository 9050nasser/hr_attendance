

import frappe
from frappe.utils import date_diff, nowdate

def execute(filters=None):
    # Validate filters
    if not filters:
        filters = {}

    conditions = []
    if filters.get("from_date"):
        conditions.append(f"la.posting_date >= '{filters.get('from_date')}'")
    if filters.get("to_date"):
        conditions.append(f"la.posting_date <= '{filters.get('to_date')}' ")
    if filters.get("department"):
        conditions.append(f"e.department = '{filters.get('department')}'")
    if filters.get("branch"):
        conditions.append(f"e.branch = '{filters.get('branch')}'")
    if filters.get("employee"):
        conditions.append(f"e.name = '{filters.get('employee')}'")

    condition_query = " AND ".join(conditions)

    # Fetch data
    data = frappe.db.sql(f"""
    SELECT 
        la.name AS leave_application_id,
        e.employee_name,
        la.leave_type,
        CONCAT(la.from_date, ' - ', la.to_date) AS leave_period,
        la.custom_approval_status as date_approved_by_tool,
        e.leave_approver AS reports_to_manager_name,
        DATEDIFF(NOW(), la.posting_date) AS days_since_submission
    FROM 
        `tabLeave Application` la
    JOIN 
        `tabEmployee` e ON la.employee = e.name
    WHERE 
        la.custom_approval_status IS NOT NULL
                         AND la.status = 'Approved'
        {f"AND {condition_query}" if condition_query else ""}
""")


    # Define columns
    columns = [
        {"label": "Leave Application ID", "fieldname": "leave_application_id", "fieldtype": "Link", "options": "Leave Application", "width": 150},
        {"label": "Employee Name", "fieldname": "employee_name", "fieldtype": "Data", "width": 150},
        {"label": "Leave Type", "fieldname": "leave_type", "fieldtype": "Data", "width": 100},
        {"label": "Leave Period", "fieldname": "leave_period", "fieldtype": "Data", "width": 150},
        {"label": "Date Approved by Tool", "fieldname": "date_approved_by_tool", "fieldtype": "Date", "width": 150},
        {"label": "Reports To Manager", "fieldname": "reports_to_manager_name", "fieldtype": "Data", "width": 150},
        {"label": "Days Since Submission", "fieldname": "days_since_submission", "fieldtype": "Int", "width": 100},
    ]
    chart_data = frappe.db.sql(f"""
        SELECT 
            COUNT(la.name) AS auto_approved_count,
            ROUND((COUNT(la.name) * 100.0 / 
                (SELECT COUNT(*) FROM `tabLeave Application` WHERE posting_date BETWEEN '{filters.get('from_date')}' AND '{filters.get('to_date')}')), 2) AS percentage_auto_approved
        FROM 
            `tabLeave Application` la
        JOIN 
            `tabEmployee` e ON la.employee = e.name
        WHERE 
            la.custom_approval_status IS NOT NULL
            {f"AND {condition_query}" if condition_query else ""}

    """, as_dict=True)

    # Add chart configuration
    chart = {
        "data": {
            "labels": ["Auto-Approved Applications"],
            "datasets": [
                {"name": "Auto-Approved Applications", "values": [row["auto_approved_count"] for row in chart_data]},
                {"name": "Percentage Auto-Approved", "values": [row["percentage_auto_approved"] for row in chart_data]},
            ],
        },
        "type": "bar",
    }
    return columns, data, None, chart
