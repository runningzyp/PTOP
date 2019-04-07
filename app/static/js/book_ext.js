$(document).ready(function () {
    var i = 1;
    $("#change").click(function () {

        if (i < 10) {
            $("body").css({
                "background-image": "url('../static/blog_back/" + i + ".png')"
            });
            i++;
        } else {
            i = 1;
        }
    });
})