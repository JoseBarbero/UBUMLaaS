let me_index = 0; // Current index of list of algorithms
let me_idexs = [0]; // List of identifier of algorithms

let med_index = 0; // Current index of list of datasets
let med_idexs = [0]; // List of identifier of datasets

let me_sub_clasifiers_count = [0];
let me_sub_filter_count = [0];

let sp_ANIMATION = false;

function me_cidex(){
    return me_idexs[me_index];
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
    function me_new_alg(){
        // First create a new block
        let nidex = me_idexs[me_idexs.length-1]+1;
        let block = $("<div></div>").addClass("maker").attr("data-idex", nidex).css("display","none");
        $.ajax({
            url: "/new_algorithm_maker",
            type: 'POST',
            contentType: 'application/x-www-form-urlencoded',
            data: "alg_type=" + $("#alg_typ").val() + "&idex="+nidex,
            success: function (result) {
                block.html(result);
                $("#makers").append(block);
                me_idexs.push(nidex);
                me_move();

                me_sub_clasifiers_count.push(0);
                me_sub_filter_count.push(0);
            }
        })
    }

    /**
     * Delete the algorithm for the current index
     */
    function me_delete_alg(){
        if(me_idexs.length == 1){
            sp_ANIMATION = false;
            launch_danger_modal("Delete error","You can't delete an algorithm if only have one");
        }else{
            let index = me_index;
            if(me_index == me_idexs.length-1){
                me_move(false, true);
            }else{
                me_move(true, true);
            }
            setTimeout(function(){
                $("div[data-idex=\""+me_idexs[index]+"\"]").remove();
                me_idexs = removeItemOnce(me_idexs, me_idexs[index]);
                me_sub_clasifiers_count.splice(index,1);
                me_sub_filter_count.splice(index,1);
                // If remove the last algorithm
                if(me_index == me_idexs.length){
                    me_index--;
                }
                if(me_idexs.length == 1){
                    $("#delete_alg").addClass("disabled");
                }
            }, 1000);   
        }
    }

    /**
     * Change the current algorithm displayed. By default move to right.
     * @param {boolean} right Direction for the movement
     * @param {boolean} deleted  If current index will be removed
     */
    function me_move(right=true, deleted=false){
        let from = me_idexs[me_index];
        let to;
        if (right){
            to = me_idexs[me_index+1];
        }else{
            to = me_idexs[me_index-1];
        }
        
        let from_block = $("div[data-idex=\""+from+"\"]");
        let to_block = $("div[data-idex=\""+to+"\"]");

        let anim;
        
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
            sp_ANIMATION=false;
        });
        to_block.toggle("slide", {direction: animIn}, "slow");
        to_block.promise().done(function(){
            sp_ANIMATION=false;
        });

        if(!deleted){
            if(right){
                me_index++;
            }else{
                me_index--;
            }
        }

    }

    $("#delete_alg").click(function(){
        if(!sp_ANIMATION){
            sp_ANIMATION=true;
            me_delete_alg();
            if(me_idexs.length == 1){
                $(this).addClass("disabled");
            }
        }
    });

    $("#before_button").click(function(){
        if(!sp_ANIMATION){
            sp_ANIMATION=true;
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

    $("#after_button").click(function(){
        if(!sp_ANIMATION){
            sp_ANIMATION=true;
            if(me_index == me_idexs.length-1){
                if($("#alg_typ").val()!=""){
                    me_new_alg();
                    $("#delete_alg").removeClass("disabled");
                }else{
                    launch_warning_modal("Add a new algorithm is not allowed","Select a algorithm type before add a new algorithm");
                    sp_ANIMATION=false;
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
});