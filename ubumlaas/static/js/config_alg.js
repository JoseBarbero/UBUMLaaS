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

function toggle_click(block){
    $("#"+block).toggle("slow");
}

function generateForm(alg_config){
    alg_config_reference = alg_config;
    var place_in = $("#form_config_alg");
    place_in.html("");
    var parameters = Object.keys(alg_config);
    var row_number = 0;
    parameters.forEach(function(i){
        row_number += 1;
        let parameter = alg_config[i];
        let row = $("<div></div>", {class: "row"});
        let block = $("<div></div>", {id: i, class: "col-12"});
        if (row_number%2 == 1){
            block.addClass("row-odd");
        }
        row.append(block);
        block.html("<label data-toggle=\"tooltip\" title=\""+parameter.help+"\" for=\""+i+"_value"+"\">"+i+"</label>");
        block.append($("<a onClick=\"toggle_click('"+i+"_value"+"')\" href=\"#a\" id=\""+i+"_open"+"\">"+
                            "<i class=\"material-icons\" style=\"float: right;\">"+
                                "arrow_drop_down_circle"+
                            "</i>"+
                       "</a>"));
        
        let content;
        switch(parameter.type){
            case "string":
                content = $("<select></select>", {id: i+"_value"});
                parameter.options.forEach(function(j){
                    content.append($("<option value=\""+j+"\">"+j+"</option>"));
                });
                break;
            case "boolean":
                let div = $("<div></div>",{class: "material-switch pull-right", id: i+"_div"});
                let label = $("<label for=\""+i+"_value"+"\" class=\"badge-primary\"></label>");
                content = $("<input/>", {type: "checkbox", id: i+"_value"});
                if (parameter.default){
                    content.attr({checked: "checked"});
                }
                div.append(content);
                div.append(label);
                content = div;
                block.children().eq(1).attr("onClick","toggle_click('"+i+"_div"+"')");
                break;
            case "float":
                content = $("<input/>", {type: 'number',
                                            step: 'any',
                                            id: i+"_value",
                                            min: convertExponentialToDecimal(parameter.min),
                                            max: convertExponentialToDecimal(parameter.max),
                                            value: parameter.default});
                break;
            case "integer":
                content = $("<input/>", {type: 'number',
                                            step: 1,
                                            id: i+"_value",
                                            min: parameter.min,
                                            max: parameter.max,
                                            value: parameter.default});
                break;
            default:
                console.log("Parameter "+i+" has unrecognized type ("+parameter.type+")");
        }
        content.attr({style: "display: none"});
        if(parameter.type != 'boolean'){
            content.addClass("form-control");
        }
        content.addClass("config_alg");
        block.append(content);
        place_in.append(row);
    });
}

function get_config_form(){
    var parameters = Object.keys(alg_config_reference);
    let result = {};
    parameters.forEach(function(i){
        let par = alg_config_reference[i];
        let parameter = $("#"+i+"_value");
        result[i] = parameter.val();
        switch(par.type){
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
    });
    return result;
}
