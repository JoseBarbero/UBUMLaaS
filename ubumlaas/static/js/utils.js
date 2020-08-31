function titleCase(str) {
   
    var splitStr = str.split("_").join(" ").toLowerCase().split(' ');
    for (var i = 0; i < splitStr.length; i++) {
        // You do not need to check if i is larger than splitStr length, as your for does that for you
        // Assign it back to the array
        splitStr[i] = splitStr[i].charAt(0).toUpperCase() + splitStr[i].substring(1);     
    }
    // Directly return the joined string
    return splitStr.join(' '); 
}

function firstClick(){
    let y = window.scrollY
    setTimeout(function(){
        $(".selectpicker").each(function(){
            $(this).next().click();
            $("body").click();
        });
        window.scrollTo(0, y)
    }, 100);

}

function removeItemOnce(arr, value) { 
    var index = arr.indexOf(value);
    if (index > -1) {
        arr.splice(index, 1);
    }
    return arr;
}
