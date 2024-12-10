frappe.ui.form.on("Attendance", {
	onload_post_render: function (frm) {
		frm.ignore_doctypes_on_cancel_all = ["Leave Ledger Entry"];
	}
})