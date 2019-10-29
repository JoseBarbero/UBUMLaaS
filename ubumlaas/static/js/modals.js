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