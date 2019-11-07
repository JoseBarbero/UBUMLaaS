$("document").ready(function(){
    colors();
    style_number = 8;
    styles = [
        "https://stackpath.bootstrapcdn.com/bootswatch/4.3.1/materia/bootstrap.min.css",
        "https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css",
        "https://stackpath.bootstrapcdn.com/bootswatch/4.3.1/cerulean/bootstrap.min.css",
        "https://stackpath.bootstrapcdn.com/bootswatch/4.3.1/cosmo/bootstrap.min.css",
        "https://stackpath.bootstrapcdn.com/bootswatch/4.3.1/cyborg/bootstrap.min.css",
        "https://stackpath.bootstrapcdn.com/bootswatch/4.3.1/darkly/bootstrap.min.css",
        "https://stackpath.bootstrapcdn.com/bootswatch/4.3.1/flatly/bootstrap.min.css",
        "https://stackpath.bootstrapcdn.com/bootswatch/4.3.1/journal/bootstrap.min.css",
        "https://stackpath.bootstrapcdn.com/bootswatch/4.3.1/litera/bootstrap.min.css",
        "https://stackpath.bootstrapcdn.com/bootswatch/4.3.1/lumen/bootstrap.min.css",
        "https://stackpath.bootstrapcdn.com/bootswatch/4.3.1/lux/bootstrap.min.css",        
        "https://stackpath.bootstrapcdn.com/bootswatch/4.3.1/minty/bootstrap.min.css",
        "https://stackpath.bootstrapcdn.com/bootswatch/4.3.1/pulse/bootstrap.min.css",
        "https://stackpath.bootstrapcdn.com/bootswatch/4.3.1/sandstone/bootstrap.min.css",
        "https://stackpath.bootstrapcdn.com/bootswatch/4.3.1/simplex/bootstrap.min.css",
        "https://stackpath.bootstrapcdn.com/bootswatch/4.3.1/sketchy/bootstrap.min.css",
        "https://stackpath.bootstrapcdn.com/bootswatch/4.3.1/slate/bootstrap.min.css",
        "https://stackpath.bootstrapcdn.com/bootswatch/4.3.1/solar/bootstrap.min.css",
        "https://stackpath.bootstrapcdn.com/bootswatch/4.3.1/spacelab/bootstrap.min.css",
        "https://stackpath.bootstrapcdn.com/bootswatch/4.3.1/superhero/bootstrap.min.css",
        "https://stackpath.bootstrapcdn.com/bootswatch/4.3.1/united/bootstrap.min.css",
        "https://stackpath.bootstrapcdn.com/bootswatch/4.3.1/yeti/bootstrap.min.css"
    ];
});

function colors(){
    let colors = ["danger", "success", "warning", "info", "secondary", "primary", "orange", "ubu-maroon"];

    colors.forEach(function(e){
        let color = getComputedStyle(document.documentElement)
            .getPropertyValue("--"+e);
        let rgba = convertHex_only_number(color, 100);
        
        document.documentElement.style.setProperty("--"+e+"-red", rgba[0]);
        document.documentElement.style.setProperty("--"+e+"-green", rgba[1]);
        document.documentElement.style.setProperty("--"+e+"-blue", rgba[2]);
    }) 
}

/**
 * Convert to rgba from hexadecimal color.
 *
 * @param {string} hex hexadecimal form of number
 * @param {int} opacity value between 0 and 1 which define alpha of color
 */
function convertHex(hex,opacity){
    let values = convertHex_only_number(hex, opacity)
    let result = 'rgba('+values[0]+','+values[1]+','+values[2]+','+values[3]+')';
    return result;
}

/**
 * Convert to rgba from hexadecimal color.
 *
 * @param {string} hex hexadecimal form of number
 * @param {int} opacity value between 0 and 1 which define alpha of color
 */
function convertHex_only_number(hex,opacity){
    hex = hex.replace('#','').trim();
    let r = parseInt(hex.substring(0,2), 16);
    let g = parseInt(hex.substring(2,4), 16);
    let b = parseInt(hex.substring(4,6), 16);

    let result = [r,g,b,opacity/100];
    return result;
}

function next_style(){
    if (style_number >= styles.length){
        style_number = 0;
    }
    $("#boostrap_css").attr("href", styles[style_number]);
    style_number++;
    setTimeout(colors,1000)
}