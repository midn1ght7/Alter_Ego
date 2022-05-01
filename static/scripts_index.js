var speed = 'slow';

$('body').hide();

var audioElement = document.createElement('audio');
audioElement.setAttribute('src', 'static/sounds/HS_SE_001.wav');

$(document).ready(function() {
    $('body').fadeIn(speed, function() {
        $('a[href], button[href]').click(function(event) {
            audioElement.play();
            var url = $(this).attr('href');
            if (url.indexOf('#') == 0 || url.indexOf('javascript:') == 0) return;
            event.preventDefault();
            $('body').hide(speed, function() {
                window.location = url;
            });
        });
    });
});

document.addEventListener("keyup", function(event) 
{
    if (event.keyCode === 13) 
    {
        audioElement.play();
        $('body').hide(speed, function() {
            window.location.href="alter_ego";
        });
    }
});