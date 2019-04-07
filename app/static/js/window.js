$(document).ready(function () {
    $('.window-show').scrollTop( $('.window-show')[0].scrollHeight );
    $(".foot-second").click(function () {
        $(".window-hidden").css("display", "block");
        $(".move").animate({
            bottom: '150px'
        });
    });

    $(".window-show").click(function (e) {
        var target = $(e.target);
        if (!target.is('.foot-second')) {
            $(".move").animate({
                bottom: '0px'
            });
        }
    })
});


