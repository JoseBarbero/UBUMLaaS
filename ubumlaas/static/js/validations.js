$("document").ready(function(){
     //Blocks
     select_dataset = $("#data");
     train_slider = $("#train_slider");
     alg_typ = $("#alg_typ");
     alg_name = $("#alg_name");
     form_dataset_configuration = $("#form_dataset_configuration");
     submit_experiment = $("#submit");
     //Mesages
     select_dataset_feedback = $("#data_feedback");
     train_slider_feedback = $("#train_slider_feedback");
     alg_typ_feedback = $("#alg_typ_feedback");
     alg_name_feedback = $("#alg_name_feedback");
     verify_all();
});

function verify_all(){
    submit_experiment.attr("disabled",true);
    invalidate = [];
    validate = [];
    let show = [];
    let hide = [];

    if (select_dataset.val() === ""){
        invalidate.push(select_dataset);
        show.push(select_dataset_feedback);
    }else{
        validate.push(select_dataset);
        hide.push(select_dataset_feedback);
    }

    if(train_slider.val() === 0){
        invalidate.push(train_slider);
        show.push(train_slider_feedback);
    }else{
        validate.push(train_slider);
        hide.push(train_slider_feedback);
    }

    if(alg_name.val() === ""){
        invalidate.push(alg_name);
        show.push(alg_name_feedback);
    }else{
        validate.push(alg_name);
        hide.push(alg_name_feedback);
    }

    if(alg_typ.val() === ""){
        invalidate.push(alg_typ);
        show.push(alg_typ_feedback);
    }else{
        validate.push(alg_typ);
        hide.push(alg_typ_feedback);
    }

    _validate(validate, hide);
    _invalidate(invalidate, show);
    if (invalidate.length == 0){
        submit_experiment.attr("disabled", false);
    }
}

function _validate(validate, hide){
    for(let i = 0; i < validate.length; i++){
        validate[i].removeClass('is-invalid')
        hide[i].css("display","none")
    }
}

function _invalidate(invalidate, show){
    for(let i = 0; i < invalidate.length; i++){
        invalidate[i].addClass('is-invalid')
        show[i].css("display","")
    }
}

