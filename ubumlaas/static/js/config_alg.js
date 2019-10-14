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

$("document").ready(function(){
    $(".open_click").click(function(e){
        e.preventDefault();
    })
})

function toggle_click(value,span){
    $("#"+span).toggle("slow");
    $("#"+value).toggle("slow");
}

function beautify_alg_config(){
    let children = $(config_fieldset.children()[0]).children();
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
            child.prepend(name_of_base_clasifier(loop))
            child.css("margin-top", (2*(loop-1))+"em");
        }
        child.addClass("col-md-"+base);
        loop++;
    });
}

function name_of_base_clasifier(level){
    let basename = get_basename("base_estimator", level-1)
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
 * Generate an base estimator configuration for ensemble.
 * 
 * @param {*} alg_name 
 */
function load_new_ensemble(alg_name, level = null){
    if(level == null){
        level = sub_clasifiers_count;
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
    generateForm(alg_config, id, level);
}

/**
 * Change validity of input attribute
 * 
 * @param {basename of input attribute}
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
 * Basename of estimator attribute
 * 
 * @param {real name of parameter} param_name 
 * @param {level of the estimator} level 
 */
function get_basename(param_name, level){
    let basename = param_name;
    if(level>0){
        basename = "level"+level+"_"+basename;
    }
    return basename;
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
function get_base_block(placein, block, param_name, param, level){
    let basename = get_basename(param_name, level);
    //Label
    let lbl = $("<label></label>", {
                                        "data-toggle": "tooltip",
                                        title: param.help,
                                        for: basename+"_value"
                                   });
    let name = document.createTextNode(param_name);
    let span = $("<span></span>", {
                                        id: basename+"_span"
                                  });
    span.text("("+param.default+")");
    lbl.append(name);
    lbl.append(span);
    //Dropdown button
    let a = $("<a></a>", {
                            onClick: "toggle_click('"+basename+"_value'"+",'"+basename+"_span'"+")",
                            href: "#a",
                            id: basename+"_open"
                         });
    let icon = $("<i></i>", {
                                class: "material-icons float-right"
                            });
    icon.text("arrow_drop_down_circle")
    a.append(icon);
    block.append(lbl);
    block.append(a);
    placein.append(block);
}

/**
 * Generate a form to configure algorithm
 * 
 * @param {algorithm object with base configuration} alg_config 
 * @param {identifier of div where form be placed} place_in_id 
 * @param {level of the estimator} level_to_modify 
 */
function generateForm(alg_config, place_in_id="form_config_alg", level_to_modify=0){
    if(level_to_modify == sub_clasifiers_count){
        sub_clasifiers_count++;
    }
    let new_subalgorithm = "";
    alg_config_reference = alg_config;
    var place_in = $("#"+place_in_id);
    place_in.html("");
    var parameters = Object.keys(alg_config);
    var row_number = 0;
    parameters.forEach(function(i){
        let basename = get_basename(i, level_to_modify);
        row_number += 1;
        let parameter = alg_config[i];
        let row = $("<div></div>", {class: "row"});
        let block = $("<div></div>", {id: basename, class: "col-12"});
        if (row_number%2 == 1){
            block.addClass("row-odd");
        }
        get_base_block(row, block, i, parameter, level_to_modify);        
        let content;
        switch(parameter.type){
            case "ensemble":
                content = $("<select></select>", {id: basename+"_value"});
                let petition = "alg_name="+$("#alg_name").val();
                let _options = give_me_base_estimators(petition);
                _options.forEach(function (e) { 
                    content.append($("<option value=\""+e.alg_name+"\">"+e.web_name+"</option>"));
                 });
                 content.val(parameter.default);
                 new_subalgorithm = parameter.default;
                 break;
            case "string":
                content = $("<select></select>", {id: basename+"_value"});
                parameter.options.forEach(function(j){
                    content.append($("<option value=\""+j+"\">"+j+"</option>"));
                });                
                break;
            case "boolean":
                let div = $("<div></div>",{class: "material-switch pull-right", id: basename+"_div"});
                let label = $("<label for=\""+basename+"_value"+"\" onClick=\"change_value('"+basename+"')\" class=\"badge-primary\"></label>");
                content = $("<input/>", {type: "checkbox", id: basename+"_value"});
                if (parameter.default){
                    content.attr({checked: "checked"});
                }
                div.append(content);
                div.append(label);
                content = div;
                block.children().eq(1).attr("onClick","toggle_click('"+basename+"_div"+"','"+basename+"_span"+"')");
                break;
            case "float":
                content = $("<input/>", {type: 'number',
                                         step: 'any',
                                         id: basename+"_value",
                                         min: convertExponentialToDecimal(parameter.min),
                                         max: convertExponentialToDecimal(parameter.max),
                                         value: parameter.default,
                                         class: "col-10 form-control"
                                        });
                content = give_me_activator(content, basename);
                block.children().eq(1).attr("onClick","toggle_click('"+basename+"_div"+"','"+basename+"_span"+"')");
                break;
            case "integer":
                content = $("<input/>", {type: 'number',
                                         step: 1,
                                         id: basename+"_value",
                                         min: parameter.min,
                                         max: parameter.max,
                                         value: parameter.default,
                                         class: "col-10 form-control"
                                        });
                content = give_me_activator(content, basename);
                block.children().eq(1).attr("onClick","toggle_click('"+basename+"_div"+"','"+basename+"_span"+"')");
                break;
            default:
                console.log("Parameter "+basename+" has unrecognized type ("+parameter.type+")");
        }
        
        content.attr({style: "display: none"});
        if(parameter.type == 'string' || parameter.type == 'ensemble'){
            content.addClass("form-control");
        }
        let func = "change_value('"+basename+"')";

        content.attr("onChange", func);
        content.addClass("config_alg");
        block.append(content);
        place_in.append(row);
        if(parameter.type == 'ensemble'){
            content.attr("onChange", "change_value('"+basename+"', true); load_next_ensemble('"+basename+"',"+(level_to_modify+1)+")");
            change_value(basename, true);
        }
        if(parameter.default == null){
            $("#"+basename+"_activator_label").click();
        }
    });
    place_in.append($("<div></div>", {class: "timeout-finished"}));
    if(new_subalgorithm != ""){
        load_new_ensemble(new_subalgorithm);
    }else if ( sub_clasifiers_count > level_to_modify){
        clean_levels(level_to_modify+1);            
    }
    beautify_alg_config();
}

function load_next_ensemble(name, level){
    let alg_name = $("#"+name+"_value").val();
    load_new_ensemble(alg_name, level);
}

/**
 * remove levels after base_level. Base level included.
 * 
 * @param {Level where start the removing} base_level 
 */
function clean_levels(base_level){
    sub_clasifiers_count = base_level-1;
    let children = $(config_fieldset.children()[0]).children();
    for(let i = base_level; i<children.length; i++){
        $(children[i]).remove();
    }
}

function give_me_activator(content, i){
    let div = $("<div></div>",{class: "row", id: i+"_div"});
    let beauty_switch = $("<div></div>",{class: "material-switch pull-right col-2", id: i+"_beauty"});
    let lbl = $("<label id=\""+i+"_activator_label\" for=\""+i+"_activator"+"\" onClick=\"change_validate('"+i+"')\" class=\"badge-danger\"></label>");
    let activator = $("<input/>", {type: "checkbox", id: i+"_activator", checked: "checked"});
    beauty_switch.append(activator);
    beauty_switch.append(lbl);
    div.append(content);
    div.append(beauty_switch);
    content = div;
    return content;
}

function get_config_form(alg_name=null, level=0){
    let name_prefix = "";
    if (level > 0){
        name_prefix = "level"+level+"_";
    }
    if(alg_name == null){
        alg_name = $("#alg_name").val();
    }
    let config = load_config(false, alg_name, false);
    var config_refence = JSON.parse(config);
    var parameters = Object.keys(config_refence);
    let result = {};
    parameters.forEach(function(i){
        let par = config_refence[i];
        let parameter = $("#"+name_prefix+i+"_value");
        if(!parameter.prop('disabled')){
            result[i] = parameter.val();    
            switch(par.type){
                case "ensemble":
                    let ens = {};
                    ens.alg_name = result[i];
                    ens.parameters = get_config_form(ens.alg_name, level+1);
                    result[i] = ens;
                    break;
                case "boolean":
                    result[i]=parameter.is(":checked");
                    break;
                case "integer":
                    result[i] = parseInt(result[i]);
                    break;
                case "float":
                    result[i] = parseFloat(result[i]);
                    break;
            }
        }
    });
    return result;
}

