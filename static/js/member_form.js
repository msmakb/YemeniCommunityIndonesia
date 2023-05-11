var childLimit = 10;
var partnerLimit = 4;
var ChdNum = 1;
var PrtNum = 1;
var addChildButton = document.getElementById("add-chd-btn");
var removeChildButton = document.getElementById("remove-chd-btn");
var addPartnerButton = document.getElementById("add-prt-btn");
var removePartnerButton = document.getElementById("remove-prt-btn");
var firstTimePhotograph = true;
var firstTimePassport = true;
var firstTimeResidency = true;

function updateFormSize() {
    let width =
        window.innerWidth ||
        document.documentElement.clientWidth ||
        document.body.clientWidth;

    let height =
        window.innerHeight ||
        document.documentElement.clientHeight ||
        document.body.clientHeight;

    let inputs = document.querySelectorAll("input");
    let select_inputs = document.querySelectorAll("select");
    for (let i = 0; i < inputs.length; i++) {
        if (width < 720) {
            inputs[i].classList.remove("form-control-sm");
            inputs[i].classList.remove("form-control-lg");
            inputs[i].classList.add("form-control-sm");
        } else {
            inputs[i].classList.remove("form-control-sm");
            inputs[i].classList.remove("form-control-lg");
            inputs[i].classList.add("form-control-lg");
        }
    }
    for (let i = 0; i < select_inputs.length; i++) {
        if (width < 720) {
            select_inputs[i].classList.remove("form-control-sm");
            select_inputs[i].classList.remove("form-control-lg");
            select_inputs[i].classList.add("form-control-sm");
        } else {
            select_inputs[i].classList.remove("form-control-sm");
            select_inputs[i].classList.remove("form-control-lg");
            select_inputs[i].classList.add("form-control-lg");
        }
    }
}

function isAgree() {
    let selectVal = document.getElementById("membership").value;
    if (selectVal == "0") {
        document.getElementById("agree").disabled = true;
    }
    if (selectVal == "1") {
        document.getElementById("agree").disabled = false;
    }
}

function addChd() {
    let a = "child";
    let b = ChdNum.toString();
    let c = a + b;

    if (ChdNum == 0) {
        removeChildButton.style.display = "block";
    }

    ChdNum++;

    let child = document.getElementById(c);
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
    let a = "child";
    let b = ChdNum.toString();
    let c = a + b;

    let child = document.getElementById(c);
    child.style.display = "none";
    if (ChdNum == 0) {
        removeChildButton.style.display = "none";
    }
}

function addPrt() {
    let a = "partner";
    let b = PrtNum.toString();
    let c = a + b;

    if (PrtNum == 0) {
        removePartnerButton.style.display = "block";
    }

    PrtNum++;

    let child = document.getElementById(c);
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
    let a = "partner";
    let b = PrtNum.toString();
    let c = a + b;

    let child = document.getElementById(c);
    child.style.display = "none";
    if (PrtNum == 0) {
        removePartnerButton.style.display = "none";
    }
}

function changePhotoReq() {
    let gender = document.getElementById("id_gender");
    let photograph = document.getElementById("id_photograph");
    if (gender.value == "0") {
        photograph.required = true;
    } else {
        photograph.required = false;
    }
}

function addPhotoModel() {
    let photograph = document.getElementById("id_photograph");
    let link = document.createElement("a");
    link.classList.add("btn");
    link.classList.add("btn-sm");
    link.classList.add("btn-outline-info");
    link.classList.add("mt-2");
    link.setAttribute("data-toggle", "modal");
    link.setAttribute("data-target", "#photoModel");
    link.innerHTML = "شروط الصورة الشخصية";
    photograph.parentNode.insertBefore(link, photograph.previousSibling);
}

function validateForm() {
    // Clear Past Validation Span
    let elements = document.querySelectorAll("span.validationError");
    for (let element of elements) {
        element.remove();
    }

    // Required Fields
    let inputs = document.querySelectorAll("input");
    let select_inputs = document.querySelectorAll("select");
    for (let i = 0; i < inputs.length; i++) {
        if (inputs[i].required == true && !inputs[i].value) {
            inputs[i].classList.add("border-danger");
            let span = document.createElement("span");
            span.classList.add("validationError");
            span.classList.add("text-danger");
            span.style.display = "block";
            span.innerHTML = "هذا الحقل مطلوب";
            inputs[i].parentNode.insertBefore(span, inputs[i].nextSibling);
        } else {
            if (inputs[i].classList.contains("border-danger")) {
                inputs[i].classList.remove("border-danger");
            }
        }
    }
    for (let i = 0; i < select_inputs.length; i++) {
        if (select_inputs[i].required == true && !select_inputs[i].value) {
            select_inputs[i].classList.add("border-danger");
            let span = document.createElement("span");
            span.classList.add("validationError");
            span.style.display = "block";
            span.innerHTML = "هذا الحقل مطلوب";
            select_inputs[i].parentNode.insertBefore(
                span,
                select_inputs[i].nextSibling
            );
        } else {
            if (select_inputs[i].classList.contains("border-danger")) {
                select_inputs[i].classList.remove("border-danger");
            }
        }
    }

    // Arabic Name Validation
    let name_ar = document.getElementById("id_name_ar");
    let pattern = /^[\u0600-\u06FF\s]+$/;
    let name_ar_has_error = false;
    if (name_ar.value && !pattern.test(name_ar.value)) {
        name_ar.classList.add("border-danger");
        let span = document.createElement("span");
        span.classList.add("validationError");
        span.style.display = "block";
        span.innerHTML = "يجب أن يحتوي هذا الحقل على أحرف عربية فقط";
        name_ar.parentNode.insertBefore(span, name_ar.nextSibling);
        name_ar_has_error = true;
    } else {
        if (name_ar.classList.contains("border-danger")) {
            name_ar.classList.remove("border-danger");
        }
    }
    if (name_ar.value && !name_ar_has_error && name_ar.value.length < 10) {
        if (name_ar.classList.contains("border-danger")) {
            name_ar.classList.add("border-danger");
        }
        let span = document.createElement("span");
        span.classList.add("validationError");
        span.style.display = "block";
        span.innerHTML = "يجب أن يحتوي الاسم على 10 أحرف على الأقل";
        name_ar.parentNode.insertBefore(span, name_ar.nextSibling);
    }

    // English Name Validation
    let name_en = document.getElementById("id_name_en");
    pattern = /^[A-Za-z\s]+$/;
    let name_en_has_error = false;
    if (name_en.value && !pattern.test(name_en.value)) {
        name_en.classList.add("border-danger");
        let span = document.createElement("span");
        span.classList.add("validationError");
        span.style.display = "block";
        span.innerHTML = "يجب أن يحتوي هذا الحقل على أحرف إنجليزية فقط";
        name_en.parentNode.insertBefore(span, name_en.nextSibling);
        name_en_has_error = true;
    } else {
        if (name_en.classList.contains("border-danger")) {
            name_en.classList.remove("border-danger");
        }
    }
    if (name_en.value && !name_en_has_error && name_en.value.length < 10) {
        if (name_en.classList.contains("border-danger")) {
            name_en.classList.add("border-danger");
        }
        let span = document.createElement("span");
        span.classList.add("validationError");
        span.style.display = "block";
        span.innerHTML = "يجب أن يحتوي الاسم على 10 أحرف على الأقل";
        name_en.parentNode.insertBefore(span, name_en.nextSibling);
    }

    // Place of Birth Name Validation
    let place_of_birth = document.getElementById("id_place_of_birth");
    pattern = /^[\u0600-\u06FF\s,-]+$/;
    if (place_of_birth.value && !pattern.test(place_of_birth.value)) {
        place_of_birth.classList.add("border-danger");
        let span = document.createElement("span");
        span.classList.add("validationError");
        span.style.display = "block";
        span.innerHTML = "يجب كتابة مكان الميلاد باللغة العربية";
        place_of_birth.parentNode.insertBefore(span, place_of_birth.nextSibling);
    } else {
        if (place_of_birth.classList.contains("border-danger")) {
            place_of_birth.classList.remove("border-danger");
        }
    }

    // Call Number Validation
    let call_number = document.getElementById("id_call_number");
    pattern = /^\d{9,15}$/;
    call_number_has_error = false;
    if (call_number.value.startsWith("00") || call_number.value.startsWith("+")) {
        if (call_number.classList.contains("border-danger")) {
            call_number.classList.add("border-danger");
        }
        let span = document.createElement("span");
        span.classList.add("validationError");
        span.style.display = "block";
        span.innerHTML = "يجب عدم إدخال المفتاح الدولي في هذا الحقل";
        call_number.parentNode.insertBefore(span, call_number.nextSibling);
        call_number_has_error = true;
    }
    if (call_number.value &&
        !call_number_has_error &&
        !pattern.test(call_number.value)
    ) {
        if (call_number.classList.contains("border-danger")) {
            call_number.classList.add("border-danger");
        }
        let span = document.createElement("span");
        span.classList.add("validationError");
        span.style.display = "block";
        span.innerHTML = "رقم الهاتف غير صحيح";
        call_number.parentNode.insertBefore(span, call_number.nextSibling);
        call_number_has_error = true;
    }

    if (!call_number_has_error &&
        call_number.classList.contains("border-danger")
    ) {
        call_number.classList.remove("border-danger");
    }

    // WA Number Validation
    let whatsapp_number = document.getElementById("id_whatsapp_number");
    pattern = /^\d{9,15}$/;
    whatsapp_number_has_error = false;
    if (whatsapp_number.value.startsWith("00") || whatsapp_number.value.startsWith("+")) {
        if (whatsapp_number.classList.contains("border-danger")) {
            whatsapp_number.classList.add("border-danger");
        }
        let span = document.createElement("span");
        span.classList.add("validationError");
        span.style.display = "block";
        span.innerHTML = "يجب عدم إدخال المفتاح الدولي في هذا الحقل";
        whatsapp_number.parentNode.insertBefore(span, whatsapp_number.nextSibling);
        whatsapp_number_has_error = true;
    }
    if (whatsapp_number.value &&
        !whatsapp_number_has_error &&
        !pattern.test(whatsapp_number.value)
    ) {
        if (whatsapp_number.classList.contains("border-danger")) {
            whatsapp_number.classList.add("border-danger");
        }
        let span = document.createElement("span");
        span.classList.add("validationError");
        span.style.display = "block";
        span.innerHTML = "رقم الهاتف غير صحيح";
        whatsapp_number.parentNode.insertBefore(span, whatsapp_number.nextSibling);
        whatsapp_number_has_error = true;
    }

    if (!whatsapp_number_has_error &&
        whatsapp_number.classList.contains("border-danger")
    ) {
        whatsapp_number.classList.remove("border-danger");
    }

    // Email Validation
    let email = document.getElementById("id_email");
    pattern = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/;
    if (email.value && !pattern.test(email.value)) {
        email.classList.add("border-danger");
        let span = document.createElement("span");
        span.classList.add("validationError");
        span.style.display = "block";
        span.innerHTML = "يجب أن يحتوي هذا الحقل على أحرف إنجليزية فقط";
        email.parentNode.insertBefore(span, email.nextSibling);
    } else {
        if (email.classList.contains("border-danger")) {
            email.classList.remove("border-danger");
        }
    }

    // Family Name Validation
    let family_name = document.getElementById("id_family_name");
    pattern = /^[\u0600-\u06FF\s]+$/;
    if (family_name.value && !pattern.test(family_name.value)) {
        family_name.classList.add("border-danger");
        let span = document.createElement("span");
        span.classList.add("validationError");
        span.style.display = "block";
        span.innerHTML = "يجب كتابة اسم العائلة باللغة العربية";
        family_name.parentNode.insertBefore(span, family_name.nextSibling);
    } else {
        if (family_name.classList.contains("border-danger")) {
            family_name.classList.remove("border-danger");
        }
    }
}

function shake(element) {
    let left = parseInt(element.style.left) || 0;
    let originalLeft = left;
    element.style.position = "relative";

    for (let i = 0; i < 3; i++) {
        setTimeout(() => {
            element.style.left = (left += 3) + "px";
        }, i * 100);
        setTimeout(() => {
            element.style.left = (left -= 3) + "px";
        }, (i + 0.5) * 100);
    }
    setTimeout(() => {
        element.style.left = originalLeft + "px";
    }, 500);
}

$("input, select").on("blur", function () {
    // Live Validation
    let hasError = false;
    $(this).next().remove("span.validationError");
    if ($(this).prop("required") &&
        (!$(this).val() ||
            $(this).val().replace(/^\s+|\s+$/g, "").length == 0)
    ) {
        // Required Input Validation
        if ($(this).attr("id") == "id_photograph" && firstTimePhotograph) {
            firstTimePhotograph = false;
        } else if ($(this).attr("id") == "id_passport_photo" && firstTimePassport) {
            firstTimePassport = false;
        } else if (
            $(this).attr("id") == "id_residency_photo" &&
            firstTimeResidency
        ) {
            firstTimeResidency = false;
        } else {
            $(this).after("<span class='validationError'>هذا الحقل مطلوب</span>");
            hasError = true;
        }
    } else if ($(this).attr("id") == "id_name_ar") {
        // Arabic Name Validation
        let pattern = /^[\u0600-\u06FF\s]+$/;
        if (!pattern.test($(this).val())) {
            $(this).after(
                "<span class='validationError'>يجب أن يحتوي هذا الحقل على أحرف عربية فقط</span>"
            );
            hasError = true;
        } else if ($(this).val().length < 10) {
            $(this).after(
                "<span class='validationError'>يجب أن يحتوي الاسم على 10 أحرف على الأقل</span>"
            );
            hasError = true;
        }
    } else if ($(this).attr("id") == "id_name_en") {
        // English Name Validation
        let pattern = /^[A-Za-z\s]+$/;
        if (!pattern.test($(this).val())) {
            $(this).after(
                "<span class='validationError'>يجب أن يحتوي هذا الحقل على أحرف إنجليزية فقط</span>"
            );
            hasError = true;
        } else if ($(this).val().length < 10) {
            $(this).after(
                "<span class='validationError'>يجب أن يحتوي الاسم على 10 أحرف على الأقل</span>"
            );
            hasError = true;
        }
    } else if ($(this).attr("id") == "id_place_of_birth") {
        // Place of Birth Validation
        let pattern = /^[\u0600-\u06FF\s,-]+$/;
        if (!pattern.test($(this).val())) {
            $(this).after(
                "<span class='validationError'>يجب كتابة مكان الميلاد باللغة العربية</span>"
            );
            hasError = true;
        }
    } else if ($(this).attr("id") == "id_date_of_birth") {
        // Date of Birth Validation
        let dateOfBirth = new Date($(this).val());
        let currentDate = new Date();
        let age = currentDate.getFullYear() - dateOfBirth.getFullYear();
        if (age < 18) {
            $(this).after(
                "<span class='validationError'>يجب أن يكون عمرك 18 عامًا على الأقل</span>"
            );
            hasError = true;
        }
    } else if ($(this).attr("id") == "id_call_number") {
        // Call Number Validation
        let pattern = /^\d{9,15}$/;
        if ($(this).val().startsWith("00") || $(this).val().startsWith("+")) {
            $(this).after(
                "<span class='validationError'>يجب عدم إدخال المفتاح الدولي في هذا الحقل</span>"
            );
            hasError = true;
        } else if (!pattern.test($(this).val())) {
            $(this).after(
                "<span class='validationError'>رقم الهاتف غير صحيح</span>"
            );
            hasError = true;
        }
    } else if ($(this).attr("id") == "id_whatsapp_number") {
        // WA Number Validation
        let pattern = /^\d{9,15}$/;
        if ($(this).val().startsWith("00") || $(this).val().startsWith("+")) {
            $(this).after(
                "<span class='validationError'>يجب عدم إدخال المفتاح الدولي في هذا الحقل</span>"
            );
            hasError = true;
        } else if (!pattern.test($(this).val())) {
            $(this).after(
                "<span class='validationError'>رقم الهاتف غير صحيح</span>"
            );
            hasError = true;
        }
    } else if ($(this).attr("id") == "id_email") {
        // Email Validation
        let pattern = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/;
        if (!pattern.test($(this).val())) {
            $(this).after(
                "<span class='validationError'>بريد إلكتروني غير صحيح</span>"
            );
            hasError = true;
        }
    } else if ($(this).attr("id") == "id_family_name") {
        // Family Name Validation
        let pattern = /^[\u0600-\u06FF\s]+$/;
        if (!pattern.test($(this).val())) {
            $(this).after(
                "<span class='validationError'>يجب كتابة اسم العائلة باللغة العربية</span>"
            );
            hasError = true;
        }
    }

    if (hasError) {
        if ($(this).hasClass("border-success")) {
            $(this).removeClass("border-success");
        }
        $(this).addClass("border-danger");
        shake(this);
    } else {
        if ($(this).hasClass("border-danger")) {
            $(this).removeClass("border-danger");
        }
        $(this).addClass("border-success");
    }
});

$(window).resize(function () {
    updateFormSize();
});

$(window).on("load", function () {
    $("#id_gender").attr("onchange", "changePhotoReq()");
    updateFormSize();
    // addPhotoModel();
    changePhotoReq();
});