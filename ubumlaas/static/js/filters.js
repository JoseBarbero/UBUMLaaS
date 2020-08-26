function load_filters(event){
    /* Mode:
     *  default: load all filters by library
     *  over_level_<num>: load all compatibles filters for level
     */
    let mode = event.data.mode;
    let idex = me_cidex();
    if (mode == "default"){
        $.ajax({
            url: event.data.url,
            type: 'POST',
            contentType: 'application/x-www-form-urlencoded',
            data: "alg_name=" + $("#alg_name_"+idex).val()+"&idex="+me_cidex(),
            success: function(result){
                $("#show_filters_"+idex).html(result);
            },
            error: function(result){
                console.log("Error");
                console.log(result);
            }
        });
    }else{
        //TODO Not necessary at the moment
    }
}

function render_filter_config(event){
    let level = event.data.level;
    //async, selected-filter, reset fieldset, filter mode
    load_config(true, null, true, true);
}

function sleep(milliseconds) {
    var start = new Date().getTime();
    for (var i = 0; i < 1e7; i++) {
      if ((new Date().getTime() - start) > milliseconds){
        break;
      }
    }
  }