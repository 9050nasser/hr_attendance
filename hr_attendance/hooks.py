app_name = "hr_attendance"
app_title = "Hr Attendance"
app_publisher = "Soultech"
app_description = "to manage attendance for employees"
app_email = "info@impact.eg"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "hr_attendance",
# 		"logo": "/assets/hr_attendance/logo.png",
# 		"title": "Hr Attendance",
# 		"route": "/hr_attendance",
# 		"has_permission": "hr_attendance.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/hr_attendance/css/hr_attendance.css"
# app_include_js = "/assets/hr_attendance/js/hr_attendance.js"

# include js, css files in header of web template
# web_include_css = "/assets/hr_attendance/css/hr_attendance.css"
# web_include_js = "/assets/hr_attendance/js/hr_attendance.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "hr_attendance/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {"Attendance" : "public/js/attendance.js",
              "Compensatory Leave Request": "public/js/compensatory_leave_request.js",
              "Leave Application" : "public/js/leave_application.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "hr_attendance/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "hr_attendance.utils.jinja_methods",
# 	"filters": "hr_attendance.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "hr_attendance.install.before_install"
# after_install = "hr_attendance.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "hr_attendance.uninstall.before_uninstall"
# after_uninstall = "hr_attendance.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "hr_attendance.utils.before_app_install"
# after_app_install = "hr_attendance.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "hr_attendance.utils.before_app_uninstall"
# after_app_uninstall = "hr_attendance.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "hr_attendance.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Attendance":{
        "before_submit": "hr_attendance.doctype_triggers.attendance.before_submit",
        "on_submit": "hr_attendance.doctype_triggers.attendance.on_submit",
        "before_cancel": "hr_attendance.doctype_triggers.attendance.on_cancel"
    },
    "Leave Application":{
        "validate": "hr_attendance.doctype_triggers.leave_application.validate"
    },
    "Compensatory Leave Request":{
        "validate":"hr_attendance.doctype_triggers.compensatory_leave_request.validate",
        "on_submit":"hr_attendance.doctype_triggers.compensatory_leave_request.on_submit",
        "on_cancel":"hr_attendance.doctype_triggers.compensatory_leave_request.on_cancel"
    }
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"hr_attendance.tasks.all"
# 	],
# 	"daily": [
# 		"hr_attendance.tasks.daily"
# 	],
# 	"hourly": [
# 		"hr_attendance.tasks.hourly"
# 	],
# 	"weekly": [
# 		"hr_attendance.tasks.weekly"
# 	],
# 	"monthly": [
# 		"hr_attendance.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "hr_attendance.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "hr_attendance.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "hr_attendance.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["hr_attendance.utils.before_request"]
# after_request = ["hr_attendance.utils.after_request"]

# Job Events
# ----------
# before_job = ["hr_attendance.utils.before_job"]
# after_job = ["hr_attendance.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"hr_attendance.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

fixtures = [
    {"dt": "Custom Field", "filters": [
        [
            "module", "in", [
                "Hr Attendance"

            ]
        ]
    ]}
]