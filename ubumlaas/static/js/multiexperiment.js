let me_index = 0; // Current index of list of algorithms
let me_idexs = [0]; // List of identifier of algorithms

let med_index = 0; // Current index of list of datasets
let med_idexs = [0]; // List of identifier of datasets

let me_sub_clasifiers_count = [0];
let me_sub_filter_count = [0];

const sp_ANIMATION = false;



function me_cidex(){
    return me_idexs[me_index];
}

function me_ciddex(){
    return med_idexs[med_index];
}

function onClickButton(idb, iddex){
    let lis = $("#sel_"+iddex+" option").filter(":selected");
    let typ = $("#alg_typ").val();
    if(lis.length > 1 && idb==="target" && !MULTITARGET.includes(typ)){
        launch_warning_modal("Only one target", "You can't select more than 1 target in no multilabel algorithms.")
    }else{
        lis.each(function(e){
            let v = $(lis[e]);
            let ids = "col" + v.attr("id").split("_")[0]
            switch(idb){
                case "use":
                    if(!v.hasClass("list-group-item-primary")){
                        $("#"+ids+"_use_label_"+iddex).click();
                    }
                    break;
                case "nuse":
                    if(v.hasClass("list-group-item-success")){
                         $("#"+ids+"_target_label_"+iddex).click();
                         //v.removeClass("list-group-item-success");
                         v.addClass("list-group-item-secondary");
                    }else if(v.hasClass("list-group-item-primary")){
                        $("#"+ids+"_use_label_"+iddex).click();
                    }
                    break;
                case "target":
                    if(!v.hasClass("list-group-item-success")){
                        $("#"+ids+"_target_label_"+iddex).click();
                    }
                    break;
            }
            v.removeAttr('selected');
            v.prop("selected", false);
        });
    }
}

/**
 * Reset the multiexperiment.
 */
    function me_reset(){

    let makers = $("#makers");
    let block = $("<div></div>").addClass("maker").attr("data-idex", 0);
    $.ajax({
        url: "/reset_multiexperiment",
        type: "POST",
        contentType: 'application/x-www-form-urlencoded',
        data: "alg_type=" + $("#alg_typ").val(),
        success: function(result){
            block.html(result);
            makers.empty();
            makers.append(block);
        }
    })

    me_index = 0;
    me_idexs = [0];

    me_sub_clasifiers_count = [0];
    me_sub_filter_count = [0];
}




$(document).ready(function(){

    /**
     * Create a new algorithm for a multiexperiment.
     * Render a new algorithms
     */
    function me_new_alg(algs=true){
        let nidex, block, url, on;
        if (algs){
            nidex = me_idexs[me_idexs.length-1]+1;
            block = $("<div></div>").addClass("maker").attr("data-idex", nidex).css("display","none");
            url = "/new_algorithm_maker"
            on = "makers"
        }else{
            nidex = med_idexs[med_idexs.length-1]+1;
            url = "/new_dataset_maker";
            on = "data-makers"
        }
        // First create a new block

        $.ajax({
            url: url,
            type: 'POST',
            contentType: 'application/x-www-form-urlencoded',
            data: "alg_type=" + $("#alg_typ").val() + "&idex="+nidex,
            success: function (result) {
                if(algs){
                    block.html(result);
                }else{
                    block = $(result);
                    block.css("display","none");
                }

                $("#"+on).append(block);
                if(algs){
                    me_idexs.push(nidex);
                    me_sub_clasifiers_count.push(0);
                    me_sub_filter_count.push(0);
                }else{
                    med_idexs.push(nidex);
                    dataset_columns.push([]);
                }

                me_move(true, false, algs);
            }
        })
    }

    /**
     * Delete the algorithm for the current index
     */
    function me_delete_alg(algs=true){
        let deletion;
        if(algs){
            deletion = "algorithm";
        }else{
            deletion = "dataset";
        }
        let idexs, index;
        if (algs){
            idexs = me_idexs;
            index = me_index;
        }else{
            idexs = med_idexs;
            index = med_index;
        }

        if(idexs.length == 1){
            //sp_ANIMATION = false;
            launch_danger_modal("Delete error","You can't delete an "+deletion+" if only have one");
        }else{
            if(index == idexs.length-1){
                me_move(false, true, algs);
            }else{
                me_move(true, true, algs);
            }
            setTimeout(function(){
                $("div[data-idex=\""+idexs[index]+"\"]").remove();
                idexs = removeItemOnce(idexs, idexs[index]);
                if(algs){
                    me_sub_clasifiers_count.splice(index,1);
                    me_sub_filter_count.splice(index,1);
                }else{
                    dataset_columns = removeItemOnce(dataset_columns, dataset_columns[index]);
                }

                // If remove the last algorithm
                if(index == idexs.length){
                    if(algs){
                        me_index--;
                    }else{
                        med_index--;
                    }

                }
                if(idexs.length == 1){
                    if(algs){
                       $("#delete_alg").addClass("disabled");
                    }else{
                       $("#delete_data").addClass("disabled");
                    }

                }
            }, 1000);   
        }
    }

    /**
     * Change the current algorithm displayed. By default move to right.
     * @param {boolean} right Direction for the movement
     * @param {boolean} deleted  If current index will be removed
     * @param {boolean} if algorithms of datasets
     */
    function me_move(right=true, deleted=false, algs = true) {
        let from, to, from_block, to_block;
        if (algs) {
            from = me_idexs[me_index];
            if (right) {
                to = me_idexs[me_index + 1];
            } else {
                to = me_idexs[me_index - 1];
            }

            from_block = $("div[data-idex=\"" + from + "\"]");
            to_block = $("div[data-idex=\"" + to + "\"]");
        }else{
            from = med_idexs[med_index];
            if (right) {
                to = med_idexs[med_index + 1];
            } else {
                to = med_idexs[med_index - 1];
            }
            from_block = $("div[data-iddex=\"" + from + "\"]");
            to_block = $("div[data-iddex=\"" + to + "\"]");
        }

        let animIn, animOut;

        if (right){
            animIn = "right";
            animOut = "left";
        }else{
            animIn = "left";
            animOut = "right";
        }
        if(deleted){
            animOut = "down";
        }
        
        from_block.toggle("slide", {direction: animOut}, "slow");
        from_block.promise().done(function(){
            //sp_ANIMATION=false;
        });
            to_block.toggle("slide", {direction: animIn}, "slow");
        to_block.promise().done(function(){
            //sp_ANIMATION=false;
        });

        if(!deleted){
            if(algs){
                if(right){
                    me_index++;
                }else{
                    me_index--;
                }
            }else{
                if(right){
                    med_index++;
                }else{
                    med_index--;
                }
            }

        }

    }

    $("#delete_alg").click(function(){
        if(!sp_ANIMATION){
            //sp_ANIMATION=true;
            me_delete_alg();
            if(me_idexs.length == 1){
                $(this).addClass("disabled");
            }
        }
    });

    $("#delete_data").click(function(){
        if(!sp_ANIMATION){
            //sp_ANIMATION=true;
            me_delete_alg(false);
            if(med_idexs.length == 1){
                $(this).addClass("disabled");
            }
        }
    });

    $("#before_button").click(function(){
        if(!sp_ANIMATION){
            //sp_ANIMATION=true;
            if(me_index != 0){
                me_move(false);
            }
            if(me_index == 0){
                $(this).addClass("disabled");
            }
            if(me_idexs.length > 1){
                $("#delete_alg").removeClass("disabled");
            }
            if(me_index < me_idexs.length-1){
                $("#after_button").children(":first").text("arrow_forward_ios");
            }
        }
    });

    $("#before_d_button").click(function(){
        if(!sp_ANIMATION){
            //sp_ANIMATION=true;
            if(med_index != 0){
                me_move(false, false, false);
            }
            if(med_index == 0){
                $(this).addClass("disabled");
            }
            if(med_idexs.length > 1){
                $("#delete_data").removeClass("disabled");
            }
            if(med_index < med_idexs.length-1){
                $("#after_d_button").children(":first").text("arrow_forward_ios");
            }
        }
    });

    $("#after_button").click(function(){
        if(!sp_ANIMATION){
            //sp_ANIMATION=true;
            if(me_index == me_idexs.length-1){
                if($("#alg_typ").val()!=""){
                    me_new_alg();
                    $("#delete_alg").removeClass("disabled");
                }else{
                    launch_warning_modal("Add a new algorithm is not allowed","Select a algorithm type before add a new algorithm");
                    //sp_ANIMATION=false;
                }
            }else{
                me_move();
            }
            if(me_index < me_idexs.length-1){
                $(this).children(":first").text("arrow_forward_ios");
            }else{
                $(this).children(":first").text("add");
            }
            $("#before_button").removeClass("disabled");
        }
    });

    $("#after_d_button").click(function(){
        if(!sp_ANIMATION){
            //sp_ANIMATION=true;
            if(med_index == med_idexs.length-1){
                me_new_alg(false);
                $("#delete_data").removeClass("disabled");
            }else{
                me_move(true, false, false);
            }
            if(med_index < med_idexs.length-1){
                $(this).children(":first").text("arrow_forward_ios");
            }else{
                $(this).children(":first").text("add");
            }
            $("#before_d_button").removeClass("disabled");
        }
    });
});