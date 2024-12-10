# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class AttendanceRule(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.attendance.doctype.early_out_penalty.early_out_penalty import EarlyOutPenalty
		from frappe.attendance.doctype.early_out_rule.early_out_rule import EarlyOutRule
		from frappe.attendance.doctype.late_in_rule.late_in_rule import LateInRule
		from frappe.attendance.doctype.late_penalty_table.late_penalty_table import LatePenaltyTable
		from frappe.types import DF

		absence_salary_component: DF.Link | None
		deduct_from_leave_balance: DF.Check
		deduct_from_salary: DF.Check
		early_out_penalty: DF.Table[EarlyOutPenalty]
		early_out_rule: DF.Table[EarlyOutRule]
		early_out_salary_component: DF.Link | None
		enable_absence_rule: DF.Check
		enable_early_out_penalty: DF.Check
		enable_early_out_rule: DF.Check
		enable_late_penalty: DF.Check
		enable_late_rule: DF.Check
		late_in_salary_component: DF.Link | None
		late_penalty_table: DF.Table[LatePenaltyTable]
		late_rule_table: DF.Table[LateInRule]
		leave_deduction_absent_factor: DF.Float
		leave_type: DF.Link | None
		salary_deduction_absent_factor: DF.Float
	# end: auto-generated types
	pass
