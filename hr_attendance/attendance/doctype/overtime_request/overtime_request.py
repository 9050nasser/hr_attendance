# Copyright (c) 2024, Soultech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate, get_last_day
from frappe.model.document import Document


class OvertimeRequest(Document):
	def on_submit(self):
		attendance_rule = self.get_attendance_rule()
		if attendance_rule.enable_overtime_fixed_amount:
			salary_component = attendance_rule.fixed_amount_salary_component
		elif attendance_rule.enable_overtime_categories:
			salary_component = attendance_rule.salary_component
		elif attendance_rule.enable_overtime_morningevening:
			salary_component = attendance_rule.morining_and_evening_salary_component
		else:
			if self.early_in:
				salary_component = attendance_rule.early_in_salary_component
			elif self.overtime_type == "Holiday Overtime":
				salary_component = attendance_rule.late_in_salary_component
			elif self.overtime_type == "Weekend Overtime":
				salary_component = attendance_rule.early_out_salary_component
			elif self.overtime_type == "Normal Overtime":
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
			payroll_date = self.date,
			amount = self.calculated_overtime_amount,
			ref_doctype = "Overtime Request",
			ref_docname = self.name
		))
		additional_salary.insert(ignore_if_duplicate=True)
		additional_salary.submit()
	def validate(self):
		existing_overtime = frappe.db.get_value("Overtime Request", {
			"name": ["!=", self.name],
			"date" : self.date,
			"employee" : self.employee,
    	})
		if existing_overtime:
			frappe.throw(_("An overtime request with this date exist {0}").format(existing_overtime))
