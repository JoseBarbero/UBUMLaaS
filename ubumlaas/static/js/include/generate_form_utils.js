/**
 * Toggle visibility of input and span field
 * 
 * @param {string} value 
 * @param {string} span 
 */
function toggle_click(value,span){
    $("#"+span).toggle("slow");
    $("#"+value).toggle("slow");
}

/**
 * Boostrap grid adaptation for multiples ensembles levels
 */
function beautify_alg_config(filter=false){
    let over = config_fieldset;
    if (filter){
        over = filter_fieldset;
    }
    let children = $(over.children()[0]).children();
    let offset = 0;
    let base = 6;
    if(children.length > 1){
        base = 4;
    }
    if (children.length < 3){
        offset = 4-children.length;
    }
    let loop = 0;
    children.each(function(e){
        let child = $(children[e]);
        child.removeAttr("class");
        if(loop == 0 && offset != 0){
            child.addClass("offset-md-"+offset);
        }
        if (loop > 0){
            child.prepend(name_of_base_clasifier(loop, filter))
            child.css("margin-top", (2*(loop-1))+"em");
        }
        child.addClass("col-md-"+base);
        loop++;
    });
}

/**
 * Generate a name of classifier 
 * 
 * @param {int} level 
 * @return {jquery node} 
 */
function name_of_base_clasifier(level, filter=false){
    let basename = get_basename("base_estimator", level-1, filter)
    if($("#"+basename+"_title").length == 0){
        let name = $("#"+basename+"_value option:selected").text();
        let block = $("<div></div>", {class: "col-12", id: basename+"_title"});
        let p = $("<p></p>", {class: "font-weight-bold center"});
        p.text(name);
        block.append(p);
        return block;
    }else{
        return $("");
    }
}

/**
 * Change span text when change for value in input.
 * 
 * @param {basename of attribute} e 
 * @param {if selectable is an ensemble} ensemble 
 */
function change_value(e, ensemble=false){
    let val;
    let value = $("#"+e+"_value");
    let span = $("#"+e+"_span");
    val = value.val()
    if(ensemble){
        val = $("#"+e+"_value option:selected").text();
    }    
    let text = "("+val+")"
    if (value.attr('type') == 'checkbox'){
        text = "("+value.is(":checked")+")"
    }
    span.text(text);
}

/**
 * Basename of estimator attribute
 * 
 * @param {real name of parameter} param_name 
 * @param {level of the estimator} level 
 */
function get_basename(param_name, level, filter=false){
    let basename = param_name;
    if(filter){
        basename += "_filter";
    }
    if(level>0){
        basename = "level"+level+"_"+basename;
    }
    return basename;
}

/**
 * remove levels after base_level. Base level included.
 * 
 * @param {Level where start the removing} base_level 
 */
function clean_levels(base_level, filter=false){
    sub_clasifiers_count = base_level-1;
    let over = config_fieldset;
    if (filter){
        over = filter_fieldset;
    }
    let children = $(over.children()[0]).children();
    for(let i = base_level; i<children.length; i++){
        $(children[i]).remove();
    }
}

/**
 * Generate the activator for numeric inputs.
 * 
 * @param {jquery node} content numeric field
 * @param {string} identifier argument id
 */
function give_me_activator(content, identifier){
    let div = $("<div></div>",{class: "row pl-2 pr-2", id: identifier+"_div"});
    let beauty_switch = $("<div></div>",{class: "material-switch pull-right col-2", id: identifier+"_beauty"});
    let lbl = $("<label id=\""+identifier+"_activator_label\" for=\""+identifier+"_activator"+"\" onClick=\"change_validate('"+identifier+"')\" class=\"badge-danger\"></label>");
    let activator = $("<input/>", {type: "checkbox", id: identifier+"_activator", checked: "checked"});
    beauty_switch.append(activator);
    beauty_switch.append(lbl);
    div.append(content);
    div.append(beauty_switch);
    content = div;
    return content;
}

/**
 * Get the base configuration of algorithm
 * 
 * @param {string} alg_name complete algorithm name
 * @param {int} level level of ensemble
 */
function get_config_form(alg_name=null, level=0, filter=false){
    let name_prefix = "";
    let name_sufix = "";
    if(filter){
        name_sufix = "_filter";
    }
    if (level > 0){
        name_prefix = "level"+level+"_";
    }
    if(alg_name == null){
        let id_ = "alg_name";
        if(filter){
            id_ = "filter_name"
        }
        alg_name = $("#"+id_).val();
    }
    let config = load_config(false, alg_name, false, filter);
    var config_refence = JSON.parse(config);
    var parameters = Object.keys(config_refence);
    let result = {};
    parameters.forEach(function(i){
        let par = config_refence[i];
        let parameter = $("#"+name_prefix+i+name_sufix+"_value");
        if(!parameter.prop('disabled')){
            result[i] = config_form_value(parameter, par, level)
        }
    });
    return result;
}

/**
    * Checks if number is in exponential format (eg: 1e-8 for 0.00000001).
    * If it does not, original number is returned.
    * If it does it converts it to string representation of that number
    * which forces it to format 0.00000001
    */
function convertExponentialToDecimal(exponentialNumber){
    // sanity check - is it exponential number
    const str = exponentialNumber.toString();
    if (str.indexOf('e') !== -1) {
        const exponent = parseInt(str.split('-')[1], 10);
        // Unfortunately I can not return 1e-8 as 0.00000001, because even if I call parseFloat() on it,
        // it will still return the exponential representation
        // So I have to use .toFixed()
        const result = exponentialNumber.toFixed(exponent);
        return result;
    } else {
        return exponentialNumber;
    }
}

/**
 * Load the next algorithm in ensemble chain
 * 
 * @param {string} name identifier of field where is the algorithm name
 * @param {int} level level of the ensemble
 */
function load_next_ensemble(name, level){
    let alg_name = $("#"+name+"_value").val();
    load_new_ensemble(alg_name, level);
}

/**
 * Generate a block to set input attribute.
 * 
 * @param {row from complete form} placein 
 * @param {row content} block 
 * @param {real name of the parameter} param_name 
 * @param {parameter object} param 
 * @param {level of the estimator} level 
 */
function get_base_block(placein, block, param_name, param, level, filter=false){
    let basename = get_basename(param_name, level, filter);
    let lbl = $("<label></label>", { "data-toggle": "tooltip",
                                     "data-placement": "left",
                                     title: param.help,
                                     for: basename+"_value" });
    let name = document.createTextNode(param_name);
    let span = $("<span></span>", { id: basename+"_span" });
    span.text("("+param.default+")");
    lbl.append(name);
    lbl.append(span);
    //Dropdown button
    let a = $("<a></a>", { onClick: "toggle_click('"+basename+"_value'"+",'"+basename+"_span'"+")",
                           href: "#a",
                           id: basename+"_open" });
    let icon = $("<i></i>", { class: "material-icons float-right" });
    icon.text("arrow_drop_down_circle")
    a.append(icon);
    block.append(lbl);
    block.append(a);
    placein.append(block);
}