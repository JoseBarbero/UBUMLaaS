$("document").ready(function(){
    $(".open_click").click(function(e){
        e.preventDefault();
    })
})

/**
 * Generate an base estimator configuration for ensemble.
 * 
 * @param {string} alg_name the name of an algorithm to be used as base estimator
 * @param {int, default=null} level of ensemble 
 */
function load_new_ensemble(alg_name, level=null, filter=false){
    if(level == null){
        level = sub_clasifiers_count;
    }
    
    if(filter){
        id = "form_config_filter_level"+level;
    }
    let id = "form_config_alg_level"+level;
    let lvl = $("#"+id);
    if(lvl.length == 0){
        lvl = $("<div></div>", {id: id});
        $(config_fieldset.children()[0]).append(lvl);
    }else{
        lvl.html("");
    }
    let alg_config = JSON.parse(load_config(false, alg_name, false));
    generateForm(alg_config, id, level, filter);
}

/**
 * Change validity of input attribute
 * 
 * @param {string} e basename of input attribute
 */
function change_validate(e){
    let _value = $("#"+e+"_value");
    if(!_value.prop('disabled')){
        _value.attr({
            disabled: "disabled"
        });
    }else{
        _value.removeAttr("disabled");
    }    
}

/**
 * Generate a form to configure algorithm.
 * 
 * @param {object} alg_config algorithm object with base configuration
 * @param {string} place_in_id identifier of div where form be placed
 * @param {int} level_to_modify level of the estimator
 */
function generateForm(alg_config, place_in_id, level_to_modify=0, filter=false){
    if (!filter){
        if(level_to_modify == sub_clasifiers_count){
            sub_clasifiers_count++;
        }
    }else{
        if(level_to_modify == sub_filter_count){
            sub_filter_count++;
        }
    }
    alg_config_reference = alg_config;
    var place_in = $("#"+place_in_id);
    place_in.html("");

    let new_subalgorithm = "";
    var parameters = Object.keys(alg_config);
    var row_number = 0;
    parameters.forEach(function(i){
        row_number += 1;
        let subalgorithm = create_algorithm_config_field(place_in, row_number, i, level_to_modify, alg_config, filter);
        if (subalgorithm != ""){
            new_subalgorithm = subalgorithm;
        }
    });
    place_in.append($("<div></div>", {class: "timeout-finished"}));
    if(new_subalgorithm != ""){
        load_new_ensemble(new_subalgorithm);
    }else if ( sub_clasifiers_count > level_to_modify){
        clean_levels(level_to_modify+1, filter);            
    }
    beautify_alg_config(filter);
    $('[data-toggle="tooltip"]').tooltip();
}

/**
 * Generate a selectable of subclasifier.
 * 
 * @param {string} basename basename of algorithm 
 * @param {object} parameter parameters of algorithm
 */
function create_ensemble_block(basename, parameter){
    let content;
    content = $("<select></select>", {id: basename+"_value"});
    let petition = "alg_name="+$("#alg_name").val()+"&exp_typ="+alg_typ.val();
    let _options = give_me_base_estimators(petition);
    _options.forEach(function (e) { 
        content.append($("<option value=\""+e.alg_name+"\">"+e.web_name+"</option>"));
     });
     content.val(parameter.default);
     
     return content;
}

/**
 * Create a switch for boolean argument.
 * 
 * @param {string} basename name of parameter in html
 * @param {object} parameter configuration of boolean argument
 */
function create_boolean_block(basename, parameter){
    let content;

    let div = $("<div></div>",{class: "material-switch pull-right", id: basename+"_div"});
    let label = $("<label for=\""+basename+"_value"+"\" onClick=\"change_value('"+basename+"')\" class=\"badge-primary\"></label>");
    content = $("<input/>", {type: "checkbox", id: basename+"_value"});
    if (parameter.default){
        content.attr({checked: "checked"});
    }
    div.append(content);
    div.append(label);
    content = div;

    return content;
}

/**
 * Create a select for string argument.
 * 
 * @param {string} basename name of parameter in html
 * @param {object} parameter configuration of string argument
 */
function create_string_block(basename, parameter){
    let content;

    content = $("<select></select>", {id: basename+"_value"});
    parameter.options.forEach(function(j){
        content.append($("<option value=\""+j+"\">"+j+"</option>"));
    });

    return content;
}

/**
 * Create a numbered input for numeric (float or integer) argument.
 * 
 * @param {string} basename name of parameter in html
 * @param {object} parameter configuration of numeric argument
 */
function create_numeric_block(basename, parameter, mode){
    let content;
    let step, min, max;
    if(mode === "float"){
        step='any';
        if(typeof parameter.min !== "undefined")
            min=convertExponentialToDecimal(parameter.min);
        if(typeof parameter.max !== "undefined")
           max=convertExponentialToDecimal(parameter.max);
    }else if(mode === 'int'){
        step=1;
        min=parameter.min;
        max=parameter.max;
    }
    content = $("<input/>", {type: 'number',
                             step: step,
                             id: basename+"_value",
                             min: min,
                             max: max,
                             value: parameter.default,
                             class: "col-10 form-control"
                        });
    content = give_me_activator(content, basename);
    return content;
}

/**
 * Define the attributes of container of algorithm configuration.
 * 
 * @param {jquery object} content 
 * @param {string} basename name of parameter in html
 */
function content_attributes(content, basename){
    content.attr({style: "display: none"});
    let func = "change_value('"+basename+"')";
    content.attr("onChange", func);
    content.addClass("config_alg");
}

/**
 * Create a container for algorithm configuration.
 * 
 * @param {string} basename name of parameter in html
 * @param {object} parameter definition of argument
 */
function create_form_fields(basename, parameter){
    let content;
    switch(parameter.type){
        case "ensemble":
            content = create_ensemble_block(basename, parameter);
            break;
        case "string":
            content = create_string_block(basename, parameter)              
            break;
        case "boolean":
            content = create_boolean_block(basename, parameter);
            break;
        case "float":
            content = create_numeric_block(basename, parameter, "float");
            break;
        case "integer":
            content = create_numeric_block(basename, parameter, "int");
            break;
        default:
            console.log("Parameter "+basename+" has unrecognized type ("+parameter.type+")");
    }
    return content;
}

/**
 * HTML+CSS+JS decoration of container of argument.
 * 
 * @param {jquery object} content 
 * @param {string} basename name of parameter in html
 * @param {object} parameter definition of argument
 * @param {integer} level_to_modify level of ensemble
 */
function final_decoration_for_form_field(content, basename, parameter, level_to_modify){
    let new_subalgorithm = "";
    if(parameter.type == 'ensemble'){
        content.attr("onChange", "change_value('"+basename+"', true); load_next_ensemble('"+basename+"',"+(level_to_modify+1)+")");
        change_value(basename, true);
        new_subalgorithm = parameter.default;
    }
    if(parameter.default == null){
        $("#"+basename+"_activator_label").click();
    }
    return new_subalgorithm;
}

/**
 * Render an algorithm argument field
 * 
 * @param {string} place_in node's identifier where put the form 
 * @param {int} row_number row index of field (for striped css)
 * @param {string} field real nome of the parameter
 * @param {int} level_to_modify level of the ensemble
 * @param {object} alg_config definition of algorithm configuration posibilities
 */
function create_algorithm_config_field(place_in, row_number, field, level_to_modify, alg_config, filter=false){
    let basename = get_basename(field, level_to_modify, filter);        
    let parameter = alg_config[field];
    let row = $("<div></div>", {class: "row"});
    let block = $("<div></div>", {id: basename, class: "col-12"});
    if (row_number%2 == 1){
        block.addClass("row-odd");
    }
    get_base_block(row, block, field, parameter, level_to_modify, filter);        
    let content = create_form_fields(basename, parameter);
    
    if(["integer", "float", "boolean"].includes(parameter.type)){
        block.children().eq(1).attr("onClick","toggle_click('"+basename+"_div"+"','"+basename+"_span"+"')");
    }else{
        content.addClass("form-control");
    }
    
    content_attributes(content, basename);        
    block.append(content);
    place_in.append(row);
    new_subalgorithm = final_decoration_for_form_field(content, basename, parameter, level_to_modify);
    return new_subalgorithm;
}

/**
 * Get the particular configuration of a field 
 * 
 * @param {jquery object} parameter 
 * @param {object} par definition of parameter
 * @param {int} level level where is the field
 */
function config_form_value(parameter, par, level){
    let result = parameter.val();
    switch(par.type){
        case "ensemble":
            let ens = {};
            ens.alg_name = result;
            ens.parameters = get_config_form(ens.alg_name, level+1);
            result = ens;
            break;
        case "boolean":
            result=parameter.is(":checked");
            break;
        case "integer":
            result = parseInt(result);
            break;
        case "float":
            result = parseFloat(result);
            break;
    }
    return result;
}