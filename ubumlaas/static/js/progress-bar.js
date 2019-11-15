const FORM_PROGRESS = $("#form_progress");

const BLOCKS_ID = ["alg_typ", "data", "config_experiment_block", "alg_name"];

const BLOCKS_ACTIVATORS = {alg_typ: "upload_dataset_block",
                           data: "config_dataset_block",
                           experiment_seed_activator: "config_experiment_block",
                           alg_name: "config_algorithm_fieldset",
                           filter_name: "config_filter_fieldset"};

already_correct = new Set([config_experiment_block]);

$("document").ready(function(){
    update_progress();
    Object.entries(BLOCKS_ACTIVATORS).forEach(function(activator){
        $("#"+activator[0]).change(function(){
            jump({data: {element:this, to: activator[1]}});
        });
    });
});

function jump(event){
    if ($(event.data.element).val() != ""){
        $("html, body").animate({
            scrollTop: $("#"+event.data.to).offset().top-$($(".navbar")[0]).height()*2
        }, 200);
    }
}

function update_progress(){
    FORM_PROGRESS.css("width",(already_correct.size/BLOCKS_ID.length*100)+"%");
}