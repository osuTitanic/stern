// https://gist.github.com/peppy/2276367
var fl = null;
var modToggle = null;
var timer;

$("document").ready(function() {
    var random = 1;

    switch (Math.floor(Math.random() * 10))
    {
        case 0:
        case 3:
            $("body").append("<div class='flashlight'></div><div class='modtoggle fl'></div>");
            modToggle = $(".modtoggle");

            fl = $(".flashlight");

            $("body").mousemove(function(e) {
                if (fl.is(":visible"))
                    fl.css('background-position', (e.pageX - 1280) + 'px ' + (e.pageY - 720 - $(document).scrollTop()) + 'px');
            });

            $(".fl").click(function(e) { fl.toggle(); });
        case 1:
        case 3:
            $("body").append("<div class='modtoggle hd'></div>");
            modToggle = $(".modtoggle");

            $("a").addClass("hiddenA");
            $(".hd").click(function() { $("a").toggleClass("hiddenA"); });
            break;
    }

    if (modToggle != null) timer = setInterval(increaseOpacity, 50);
});

var currOpacity = 0;
function increaseOpacity()
{
    currOpacity += 0.01;
    if (currOpacity >= 0.90)
    {
        currOpacity = 0.90;
        clearInterval(timer);
    }

    if (fl != null)
    {
        fl.css('opacity',currOpacity);
        modToggle.css('opacity', currOpacity < 0.9 ? 0 : currOpacity);
    }
    else
    {
        modToggle.css('opacity', currOpacity);
    }
}