const MULTITARGET = ["MultiClassification", "MultiRegression"];

function only_one_target(target){
    let typ = $("#alg_typ").val();
    if (!MULTITARGET.includes(typ)){
        let target_candidates = $(".col_target");
        target_candidates.each(function(){
            if($(this).attr("id")!=target){
                $(this).prop("checked",false);
                let ido = $("#"+$(this).attr("id").split("_")[0].split("col")[1] + "_opt");
                if(ido.hasClass("list-group-item-success")){
                    ido.removeClass("list-group-item list-group-item-success");
                    ido.addClass("list-group-item list-group-item-secondary");
                }
            }
        });
    }
}

function target_or_use(identifier, mode){
    let id = identifier.split("col")[1];
    let use = $("#"+identifier+"_use");
    let target = $("#"+identifier+"_target");
    let v = $("#"+id+"_opt");
    v.removeClass("list-group-item-primary list-group-item-secondary list-group-item-success");
    if (mode == "target"){
        if(use.is(":checked")){
            use.prop("checked", false);
        }
        v.addClass("list-group-item-success");
    }else if(mode == "use"){
        if(target.is(":checked")){
            target.prop("checked", false);
        }
        if(!use.is(":checked")){
            v.addClass("list-group-item-primary");
        }else{
            v.addClass("list-group-item-secondary");
        }
    }
}

function get_dataset_config(){
    let typ = $("#alg_typ").val();
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
   
    dataset_config.target = [];
    
    for(var i=0; i<columns.length; i++){
        var current_column = dataset_columns[i];
        var use = $("#col"+i+"_use");
        var target = $("#col"+i+"_target");
        if (target.is(":checked")){

            dataset_config.target.push(current_column);

        }else if(use.is(":checked")){
            selected_columns.push(current_column);
        }
    }
    dataset_config.columns = selected_columns;
    return dataset_config;
}