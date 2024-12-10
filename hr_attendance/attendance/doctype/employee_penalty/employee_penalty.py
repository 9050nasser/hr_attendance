# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, get_last_day


class EmployeePenalty(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		amount: DF.Currency
		days: DF.Float
		employee: DF.Link
		employee_name: DF.Data | None
		penalty_amount: DF.Currency
		penalty_date: DF.Date
		penalty_type: DF.Literal["", "Amount", "Days"]
		reason: DF.Literal["Late In", "Early Out", "Absence", "Other"]
	# end: auto-generated types
	def on_submit(self):
		attendance_rule = self.get_attendance_rule()
		if self.reason == "Late In":
			salary_component = attendance_rule.late_in_salary_component
		elif self.reason == "Early Out":
			salary_component = attendance_rule.early_out_salary_component
		elif self.reason == "Absence":
			salary_component = attendance_rule.absence_salary_component
		
		self.make_additional_salary(salary_component)
	def get_attendance_rule(self):
		attendance_rule_name = frappe.db.get_value("Employee", self.employee, "custom_attendance_rule")
		if attendance_rule_name:
			return frappe.get_doc("Attendance Rule", attendance_rule_name)
		else:
			frappe.throw(_("Employee {0} is not linked with attendance rule").format(self.employee))

	def make_additional_salary(self, salary_component):
		additional_salary = frappe.get_doc(dict(
			doctype = "Additional Salary",
			employee = self.employee,
			salary_component = salary_component,
			payroll_date = self.penalty_date,
			amount = self.penalty_amount,
			ref_doctype = "Employee Penalty",
			ref_docname = self.name
		))
		additional_salary.insert(ignore_if_duplicate=True)
		additional_salary.submit()