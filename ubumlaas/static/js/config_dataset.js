function only_one_target(target){
    let target_candidates = $(".col_target");
    target_candidates.each(function(){
        if($(this).attr("id")!=target){
            $(this).prop("checked",false);
        }
    });
}

function target_or_use(identifier, mode){
    let use = $("#"+identifier+"_use");
    let target = $("#"+identifier+"_target");
    if (mode == "target"){
        if(use.is(":checked")){
            use.prop("checked", false);
        }
    }else if(mode == "use"){
        if(target.is(":checked")){
            target.prop("checked", false)
        }
    }
}

