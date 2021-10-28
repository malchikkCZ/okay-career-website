$('.respicon').on('tap mouseover click', function () {
    if ($('.respmenu').css("display") == "block") {
        $('.respmenu').css("display", "none");
    } else {
        $('.respmenu').css("display", "block");
    }
});

$(document).on('tap click', function (evt) {
    if (!$(evt.target).hasClass('respmenu')) {
        $('.respmenu').css("display", "none");
    }
});

$('.respmenu').on('mouseout', function () {
    $('.respmenu').css("display", "none");
});