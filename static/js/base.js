$(function () {
    $('form').on('submit', function (e) {
        document.body.classList.add("posting");
        document.getElementById("loading-screen").style.display = "block";
        document.getElementById("screen").classList.add("blur");
    });
})
