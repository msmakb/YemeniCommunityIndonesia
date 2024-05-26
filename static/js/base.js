$(function () {
    $('form').on('submit', function (e) {
        document.body.classList.add("posting");
        document.getElementById("loading-screen").style.display = "block";
        document.getElementById("screen").classList.add("blur");
    });
})

var sidenav = document.getElementById("sidenav");
var toggleNavBarButton = document.getElementById("toggle-btn");
var sideNavBarStatus = 0;
var opening = false;

$(function () {
    $('form').on('submit', function (e) {
        document.body.classList.add("posting");
    });
})

function toggleSideNav() {
    if (sideNavBarStatus == 0) {
        sidenav.classList.add("sidenav-open");
        sideNavBarStatus = 1;
        opening = true;
    } else {
        sidenav.classList.remove("sidenav-open");
        sideNavBarStatus = 0;
    }
}

$(window).resize(function () {
    let width =
        window.innerWidth ||
        document.documentElement.clientWidth ||
        document.body.clientWidth;

    if (width > 767 && sidenav.classList.contains("sidenav-open")) {
        sidenav.classList.remove("sidenav-open");
        sideNavBarStatus = 0;
    }
});

window.onscroll = function () {
    sideNavBarStatus = 0;
    if (sidenav.classList.contains("sidenav-open")) {
        sidenav.classList.remove("sidenav-open");
    }
};

window.addEventListener('click', function (e) {
    if (!opening && sideNavBarStatus == 1 && !sidenav.contains(e.target)) {
        sidenav.classList.remove("sidenav-open");
        sideNavBarStatus = 0;
    }
    opening = false;
});