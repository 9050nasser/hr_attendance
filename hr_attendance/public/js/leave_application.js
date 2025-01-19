frappe.ui.form.on("Leave Application", {
    employee:function(frm){
        get_skipped_allocation_leaves(frm)
    },
    onload_post_render: function(frm){
        if(frm.doc.employee){
            get_skipped_allocation_leaves(frm)
        }
    },
    onload: function(frm){
        if(frm.doc.employee){
            get_skipped_allocation_leaves(frm)
        }
    },
    from_date: function(frm){
        if(frm.doc.employee){
            get_skipped_allocation_leaves(frm)
        }
    },
    to_date: function(frm){
        if(frm.doc.employee){
            get_skipped_allocation_leaves(frm)
        }
    },
    refresh: function(frm){
        if(frm.doc.employee){
            get_skipped_allocation_leaves(frm)
        }
    }
})
function get_skipped_allocation_leaves(frm){
    frappe.call({
        method: "hr_attendance.doctype_triggers.leave_application.get_skipped_allocation_leaves",
        callback:function(r){
        if(r.message){
            let additional_leaves = r.message.map(row=>row.name)
            let leaves = frm.fields_dict.leave_type.get_query().filters[0]
            let new_leaves = [...additional_leaves, ...leaves[2]]
            leaves[2] = new_leaves
            frm.set_query("leave_type", function(){
            return {
                filters:[leaves]
            }
            })
        }
        }
    })
}