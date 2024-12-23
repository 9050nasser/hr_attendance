frappe.ui.form.on("Compensatory Leave Request",{
    work_end_date: function(frm){
        // get attendance value depends on the employee and work_from_date
        frappe.call({
            method: "hr_attendance.doctype_triggers.compensatory_leave_request.get_attendance_name",
            args:{
                employee: frm.doc.employee,
                attendance_date: frm.doc.work_from_date
            },
            callback: function(r){
                if(r.message){
                    frm.set_value("custom_worked_on_holiday", r.message)
                }else{
                    frappe.throw(__("No Attendance record found"))
                }
            }
        })
    }
})