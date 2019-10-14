function only_one_target(target){
    let target_candidates = $(".col_target");
    target_candidates.each(function(){
        if($(this).attr("id")!=target){
            $(this).prop("checked",false);
        }
    });
}

function target_or_use(identifier, mode){
    let use = $("#"+identifier+"_use");
    let target = $("#"+identifier+"_target");
    if (mode == "target"){
        if(use.is(":checked")){
            use.prop("checked", false);
        }
    }else if(mode == "use"){
        if(target.is(":checked")){
            target.prop("checked", false)
        }
    }
}

function get_dataset_config(){
    dataset_config = {}
    let mode = $("input[type=radio][name=experiment_mode]:checked").val();
    dataset_config.mode = mode;
    switch(mode){
        case "cross":
            dataset_config.k_folds = parseInt($("#k_folds").val());
            break;
        case "split":
            dataset_config.train_partition = parseInt($("#train_slider").val());
            break;
    }
    let selected_columns = [];
    let columns = $(".column-dataset");
    for(var i=0; i<columns.length; i++){
        var current_column = dataset_columns[i];
        var use = $("#col"+i+"_use");
        var target = $("#col"+i+"_target");
        if (target.is(":checked")){
            dataset_config.target = current_column;
        }else if(use.is(":checked")){
            selected_columns.push(current_column);
        }
    }
    dataset_config.columns = selected_columns;
    return dataset_config;
}