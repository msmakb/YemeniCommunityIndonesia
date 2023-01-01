let childLimit = 10;
let partnerLimit = 4;
let ChdNum = 1;
let PrtNum = 1;
var addChildButton = document.getElementById("add-chd-btn");
var removeChildButton = document.getElementById("remove-chd-btn");
var addPartnerButton = document.getElementById("add-prt-btn");
var removePartnerButton = document.getElementById("remove-prt-btn");




function updateFormSize() {
    var width = window.innerWidth ||
        document.documentElement.clientWidth ||
        document.body.clientWidth;

    var height = window.innerHeight ||
        document.documentElement.clientHeight ||
        document.body.clientHeight;

    var inputs = document.querySelectorAll('input');

    for (var i = 0; i < inputs.length; i++) {
        if (width < 720) {
            inputs[i].classList.remove('form-control-sm');
            inputs[i].classList.remove('form-control-lg');
            inputs[i].classList.add('form-control-sm');
        } else {
            inputs[i].classList.remove('form-control-sm');
            inputs[i].classList.remove('form-control-lg');
            inputs[i].classList.add('form-control-lg');
        }
    }

    console.log(width);
    console.log(height);


}

function isAgree() {
    var selectVal = document.getElementById("membership").value;
    if (selectVal == "0") {
        document.getElementById("agree").disabled = true;
    }
    if (selectVal == "1") {
        document.getElementById("agree").disabled = false;
    }

}


function addChd() {
    let a = 'child';
    let b = ChdNum.toString();
    let c = a + b;

    if (ChdNum == 0) {
        removeChildButton.style.display = "block";
    }

    ChdNum++;

    var child = document.getElementById(c);
    child.style.display = "block";

    if (ChdNum == childLimit) {
        addChildButton.style.display = "none";
    }
}

function removeChd() {
    if (ChdNum == childLimit) {
        addChildButton.style.display = "block";
    }

    ChdNum--;
    let a = 'child';
    let b = ChdNum.toString();
    let c = a + b;

    var child = document.getElementById(c);
    child.style.display = "none";
    if (ChdNum == 0) {
        removeChildButton.style.display = "none";
    }
}

function addPrt() {
    let a = 'partner';
    let b = PrtNum.toString();
    let c = a + b;

    if (PrtNum == 0) {
        removePartnerButton.style.display = "block";
    }

    PrtNum++;

    var child = document.getElementById(c);
    child.style.display = "block";

    if (PrtNum == partnerLimit) {
        addPartnerButton.style.display = "none";
    }
}

function removePrt() {
    if (PrtNum == partnerLimit) {
        addPartnerButton.style.display = "block";
    }

    PrtNum--;
    let a = 'partner';
    let b = PrtNum.toString();
    let c = a + b;

    var child = document.getElementById(c);
    child.style.display = "none";
    if (PrtNum == 0) {
        removePartnerButton.style.display = "none";
    }
}

updateFormSize();
window.addEventListener("resize", updateFormSize);
