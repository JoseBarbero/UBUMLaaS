/**
 * Generate a launch_alert_modal
 * 
 * @param {string} title 
 * @param {html node} body 
 */
function launch_alert_modal(title, text, title_class=null, after=null){
    let body = $("<p></p>");
    body.text(text);

    $("#alert_modal_label").text(title);
    $("#alert_modal_body").html("").append(body);

    if(title_class !== null){
        $("#alert_modal_label").addClass(title_class);
    }

    $("#alert_modal").modal({
        show: true
    });

    if(after !== null){
        $("#alert_modal").on("hide.bs.modal", after)
    }
}

function launch_danger_modal(title, text, after=null){
    launch_alert_modal("❌ "+title, text, "text-danger font-weight-bold", after)
}

function launch_warning_modal(title, text, after=null){
    launch_alert_modal("⚠️ "+title, text, "text-warning font-weight-bold", after)
}

function launch_confirm_modal(title, text, func, args, title_class=null){
    let body = $("<p></p>");
    body.text(text);
 
    $("#confirm_modal_label").text(title);
    $("#confirm_modal_body").html("").append(body);

    if(title_class !== null){
        $("#confirm_modal_label").addClass(title_class);
    }
    $("#confirm_modal_confirm").off("click");
    $("#confirm_modal_confirm").click(function(){
        func(args);
    })

    $("#confirm_modal").modal({
        show: true
    });

    
}

function launch_confirm_danger_modal(title, text, func, args){
    launch_confirm_modal("❌ "+title, text, func, args, "text-danger font-weight-bold")
}