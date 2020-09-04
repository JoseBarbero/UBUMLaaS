/**
 * Possible values of multitarget algorithms
 */
const MULTITARGET = ["MultiClassification"];

/**
 * Possible values of Non-Supervised algorithms
 */
const UNSUPERVISED = ["Clustering"]


/**
 * It guarantees only one target if algorithms is not MULTITARGET 
 * And not target allowed in UNSUPERVISED
 * 
 * @param {string} target identifier of target selected
 * @param {int} External identifier for dataset
 */
function only_one_target(target, iddex){
    let typ = $("#alg_typ").val();
    if(UNSUPERVISED.includes(typ)){
        $("#"+target).prop("checked", true);
        launch_danger_modal("Target not allowed",
                            "Algorithms of the type "+typ+" are unsupervised, therefore, they not allow targets");
    }
    else if (!MULTITARGET.includes(typ)){
        let target_candidates = $(".col_target[id$='"+iddex+"']");
        target_candidates.each(function(){
            if($(this).attr("id")!=target){
                $(this).prop("checked",false);
                let ido = $("#"+$(this).attr("id").split("_")[0].split("col")[1] + "_opt_"+iddex);
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
 * @param {int} identifier for the dataset in external form
 */
function target_or_use(identifier, mode, iddex){
    let typ = $("#alg_typ").val();
    if(!UNSUPERVISED.includes(typ) || mode == "use"){
        let id = identifier.split("col")[1];
        let use = $("#"+identifier+"_use_"+iddex);
        let target = $("#"+identifier+"_target_"+iddex);
        let v = $("#"+id+"_opt_"+iddex);
        v.removeClass("list-group-item-primary list-group-item-secondary list-group-item-success");
        if (mode == "target"){
            if(use.is(":checked")){
                use.prop("checked", false);
            }
            if(!target.is(":checked")){
                v.addClass("list-group-item-success")
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

    dataset_config.columns = [];
    dataset_config.target = [];
    for (let iddex = 0; iddex < med_idexs.length; iddex++){
        let idex = med_idexs[iddex];
        let tget = [];
        let scolumn = [];
        for(let i=0; i<dataset_columns[iddex].length; i++){
            var current_column = dataset_columns[iddex][i];
            var use = $("#col"+i+"_use_"+idex);
            var target = $("#col"+i+"_target_"+idex);
            if (target.is(":checked")){
                tget.push(current_column);
            }else if(use.is(":checked")){
                scolumn.push(current_column);
            }
        }
        dataset_config.columns.push(scolumn);
        dataset_config.target.push(tget);
    }
    if (med_idexs.length == 1){
        dataset_config.columns = dataset_config.columns[0];
        dataset_config.target = dataset_config.target[0];
    }

    let r_s = $("input[type=radio][name=seed_or_repetition]:checked").val();
    switch(r_s){
        case "part_seed":
            random_seed = $("#experiment_seed_value");
            dataset_config.random_seed = random_seed.attr("disabled") ? null : parseInt(random_seed.val());
            break;
        case "repetition":
            dataset_config.repetition = parseInt($("#repetition_value").val());
            break;
    }


    dataset_config.alg_type = alg_typ.val();
    return dataset_config;
}

