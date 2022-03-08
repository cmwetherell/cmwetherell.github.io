var gInd = false
var aInd = false
var rInd = false
var mInd = false

function gaClick(elem) {
    if(!aInd&!gInd){
        if(elem.id == "anish"){
            gInd = !gInd
        } else {
            aInd = !aInd
        }
    } else {
        aInd = !aInd
        gInd = !gInd

    }

    if(aInd){
        document.getElementById("dmitry").classList.remove("strike");
    } else{
        document.getElementById("dmitry").classList.add("strike");
    }

    if(gInd){
        document.getElementById("anish").classList.remove("strike");
    } else{
        document.getElementById("anish").classList.add("strike");
    }

    $('.begin').hide();
    $('.ar').hide();
    $('.dr').hide();
    $('.am').hide();
    $('.dm').hide();

    if(gInd & rInd){
        $('.ar').show();
    } else if (gInd & mInd) {
        $('.am').show();
    } else if (aInd & rInd) {
        $('.dr').show();
    } else if (aInd & mInd) {
        $('.dm').show();
    } else {$('.begin').show();}
}

function rmClick(elem) {
    if(!rInd&!mInd){
        if(elem.id == "richard"){
            rInd = !rInd
        } else {
            mInd = !mInd
        }
    } else {

    rInd = !rInd
    mInd = !mInd

    }

    if(rInd){
        document.getElementById("richard").classList.remove("strike");
    } else{
        document.getElementById("richard").classList.add("strike");
    }

    if(mInd){
        document.getElementById("maxime").classList.remove("strike");
    } else{
        document.getElementById("maxime").classList.add("strike");
    }

    $('.begin').hide();
    $('.ar').hide();
    $('.dr').hide();
    $('.am').hide();
    $('.dm').hide();

    if(gInd & rInd){
        $('.ar').show();
    } else if (gInd & mInd) {
        $('.am').show();
    } else if (aInd & rInd) {
        $('.dr').show();
    } else if (aInd & mInd) {
        $('.dm').show();
    } else {$('.begin').show();}
}