function load_filters(event){
    /* Mode:
     *  default: load all filters by library
     *  over_level_<num>: load all compatibles filters for level
     */
    let mode = event.data.mode;
    if (mode == "default"){
        $.ajax({
            url: event.data.url,
            type: 'POST',
            contentType: 'application/x-www-form-urlencoded',
            data: "alg_name=" + $("#alg_name").val(),
            success: function(result){
                $("#show_filters").html(result);
            },
            error: function(result){
                console.log("Error");
                console.log(result);
            }
        });
    }else{
        //TODO
    }
}

function render_filter_config(event){
    let level = event.data.level;
    //async, selected-filter, reset fieldset, filter mode
    load_config(true, null, true, true);
}