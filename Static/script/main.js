$('#sup_password').on('focusin', () => {
    $('.pass-needs').slideDown(500);
}).on('focusout', () => {
    $('.pass-needs').slideUp(500);
}).on('input', () => {
    let pass = $("#sup_password").val();
    let passLength = pass.length;
    let passUpper = /[A-Z]/.test(pass);
    let passLower = /[a-z]/.test(pass);
    let passNum = /[0-9]/.test(pass);
    let passSpecial = /[^A-Za-z0-9]/.test(pass);
    if (passLength >= 8) {
        $(".length-req").addClass("pass-req-check")
        $(".length-req ion-icon").attr("name", "checkmark-outline")
    }
    else{
        $(".length-req").removeClass("pass-req-check")
        $(".length-req ion-icon").attr("name", "close-outline")
    }
    if (passUpper) {
        $(".upper-req").addClass("pass-req-check")
        $(".upper-req ion-icon").attr("name", "checkmark-outline")
    }
    else{
        $(".upper-req").removeClass("pass-req-check")
        $(".upper-req ion-icon").attr("name", "close-outline")
    }
    if (passLower) {
        $(".lower-req").addClass("pass-req-check")
        $(".lower-req ion-icon").attr("name", "checkmark-outline")
    }
    else{
        $(".lower-req").removeClass("pass-req-check")
        $(".lower-req ion-icon").attr("name", "close-outline")
    }
    if (passNum) {
        $(".num-req").addClass("pass-req-check")
        $(".num-req ion-icon").attr("name", "checkmark-outline")

    }
    else{
        $(".num-req").removeClass("pass-req-check")
        $(".num-req ion-icon").attr("name", "close-outline")
    }
    if (passSpecial) {
        $(".spec-req").addClass("pass-req-check")
        $(".spec-req ion-icon").attr("name", "checkmark-outline")
    }
    else{
        $(".spec-req").removeClass("pass-req-check")
        $(".spec-req ion-icon").attr("name", "close-outline")
    }
});