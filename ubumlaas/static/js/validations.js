$("document").ready(function(){
    load_verify_elements();
    submit_button_change(true, "secondary");
});

function load_verify_elements(){
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
    //Conditions
    verify_conditions = ["",0,"",""];
}

/**
 * Verify if experiments is configured correctly.
 * If any verification failed submit button will be disables.
 */
function verify_all(element=null){
    load_verify_elements();
    submit_button_change(true, "secondary");
    let invalidate = [];
    let validate = [];
    let show = [];
    let hide = [];
    select_dataset = $("#data"); //Is necesary reload it
    let elements = [select_dataset, train_slider, alg_typ, alg_name];
    let elements_feedback = [select_dataset_feedback, train_slider_feedback, alg_typ_feedback, alg_name_feedback];
    for(let i=0; i<elements.length; i++){
        if(elements[i].val() == null || elements[i].val() === verify_conditions[i]){
            _add(invalidate, show, elements[i], elements_feedback[i]);
        }else{            
            _add(validate, hide, elements[i], elements_feedback[i]);
        }
    }
  
    _validate_or_invalidate(validate, hide, true, element);
    _validate_or_invalidate(invalidate, show, false, element);
    if (invalidate.length == 0){
        submit_button_change(false, "primary");
    }
}

function submit_button_change(disabled, btn){
    let css = "btn btn-"+btn+" btn-block btn-lg mt-4";
    submit_experiment.attr("disabled", disabled);
    submit_experiment.removeClass();
    submit_experiment.addClass(css);
}

/**
 * Add input widget to a list.
 * 
 * @param {list} elements_list list of input widgets 
 * @param {list} feedback_list list of feedbacks of input widgets
 * @param {html node} element input widget
 * @param {hmlt node} feedback feedback of input widget
 */
function _add(elements_list, feedback_list, element, feedback){
    elements_list.push(element);
    feedback_list.push(feedback);
}

/**
 * Show feedback of invalid inputs.
 * 
 * @param {list} input list of inputs to feedback as invalid.
 * @param {list} label list of labels to feedback as invalid.
 */
function _appear(input, label){
    input.addClass('is-invalid');
    label.css("display","");
}

/**
 * Set inputs as valid.
 * 
 * @param {list} input list of inputs to feedback as valid.
 * @param {list} label list of labels to feedback as valid.
 */
function _disappear(input, label){
    input.removeClass('is-invalid');
    label.css("display","none");
}

/**
 * Discriminator of funtions between show or unshow validation feedbacks.
 * 
 * @param {list} input_list list of input widgets
 * @param {list} label_list list of input feedbacks
 * @param {boolean} opt true if valid, false if not. 
 * @param {input_name} element if not null then modify only element
 */
function _validate_or_invalidate(input_list, label_list, opt, element){
    for(let i = 0; i < input_list.length; i++){
        if(element == null || input_list[i].attr("id") == element){
            if(opt)
                _disappear(input_list[i], label_list[i]);
            else
                _appear(input_list[i], label_list[i]);
        }
    }
}

