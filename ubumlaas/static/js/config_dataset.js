/**
 * Possible values of multitarget algorithms
 */
const MULTITARGET = ["MultiClassification", "MultiRegression"];

/**
 * It guarantees only one target if algorithms is not MULTITARGET 
 * 
 * @param {string} target identifier of target selected 
 */
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

/**
 * It guarantee than column selected as target cannot be use, and vice versa.
 * 
 * @param {string} identifier of column 
 * @param {string} mode value between target or use
 */
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
        if(!target.is(":checked")){
            v.addClass("list-group-item-success");
        }else{
            v.addClass("list-group-item-secondary");
        }
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

/**
 * Get the final configuration of the dataset.
 * 
 * @return {object} {mode:"cross|split", target:["column names"], columns:["column names"], random_seed: null|number}
 */
function get_dataset_config(){
    let dataset_config = {}
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

    random_seed = $("#experiment_seed_value");
    dataset_config.random_seed = random_seed.attr("disabled") ? null : parseInt(random_seed.val());
    return dataset_config;
}