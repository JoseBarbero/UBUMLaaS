$("document").ready(function(){

    let colors = ["danger", "success", "warning", "info", "secondary", "primary"];

    colors.forEach(function(e){
        let color = getComputedStyle(document.documentElement)
            .getPropertyValue("--"+e);
        let rgba = convertHex_only_number(color, 100);
        
        document.documentElement.style.setProperty("--"+e+"-red", rgba[0]);
        document.documentElement.style.setProperty("--"+e+"-green", rgba[1]);
        document.documentElement.style.setProperty("--"+e+"-blue", rgba[2]);
    })    
});

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