const imagePath = '/static/background';
const totalFrames = 150;
const animationDuration = 1300;
const timePerFrame = animationDuration / totalFrames;
let timeWhenLastUpdate;
let timeFromLastUpdate;
let frameNumber = 1;

// 'step' function will be called each time browser rerender the content
// we achieve that by passing 'step' as a parameter to the 'requestAnimationFrame' function
function step(startTime) {
  // 'startTime' is provided by requestAnimationName function, and we can consider it as current time
  // first of all we calculate how much time has passed from the last time when frame was update
  if (!timeWhenLastUpdate) timeWhenLastUpdate = startTime;
  timeFromLastUpdate = startTime - timeWhenLastUpdate;
  
  // then we check if it is time to update the frame
  if (timeFromLastUpdate > timePerFrame) {
    // and update it accordingly
    $("#background").attr({src: imagePath + `/bg_${frameNumber}.jpeg`});

    // reset the last update time
    timeWhenLastUpdate = startTime;
    
    // then increase the frame number or reset it if it is the last frame
    if (frameNumber >= totalFrames) {
      frameNumber = 1;
    } else {
      frameNumber = frameNumber + 1;
    }        
  }
  requestAnimationFrame(step);
}

// create a set of hidden divs
// and set their background-image attribute to required images
// that will force browser to download the images
$(document).ready(() => {
  for (var i = 1; i < totalFrames + 1; i++) {
    $('body').append(`<div id="preload-image-${i}" style="background-image: url('${imagePath}/bg_${i}.jpeg');"></div>`);
  }
});

$(document).ready(function()
{
    var count = 0;
    var voice_busy = false;
    var audioElement = document.createElement('audio');

    let audioIN = { audio: true };
    //  audio is true, for recording
  
    // Access the permission for use
    // the microphone
    navigator.mediaDevices.getUserMedia(audioIN)
    // 'then()' method returns a Promise
    .then(function (mediaStreamObj) {

        let mediaRecorder = new MediaRecorder(mediaStreamObj);
        document.addEventListener("keyup", function(event) 
        {
            if (event.keyCode === 145) 
            {
                if (voice_busy == true)
                {
                    voice_busy = false;
                    mediaRecorder.stop();
                    console.log(mediaRecorder.state);
                }
                else
                {
                    voice_busy = true;
                    mediaRecorder.start();
                    console.log(mediaRecorder.state);
                    $.get("/listening", $(this).serialize())
                    .done(function(data) 
                    {
                        response(data.message, data.sprite, data.sound, data.new_name);
                    })
                    .fail(function() 
                    {
                        $("#output_text").html("An error has occurred.");
                    });
                }
            }
        })

        // Chunk array to store the audio data 
        let dataArray = [];

        // If audio data available then push 
        // it to the chunk array
        mediaRecorder.ondataavailable = function (ev) 
        {
            if (ev.data.size > 0)
            {
                console.log("data available");
                dataArray.push(ev.data);
            }
            else
            {
                console.log("data empty");
            }
        }
        
    
        // Convert the audio data in to blob 
        // after stopping the recording
        mediaRecorder.onstop = function (ev) 
        {
            // blob of type mp3
            let audioData = new Blob(dataArray, { 'type' : 'audio/wav; codecs=0' });
            console.log(audioData);

            // After fill up the chunk 
            // array make it empty
            dataArray = [];

            var form = new FormData();
            form.append('file', audioData, 'recording.wav');
            
            $.ajax({
              type: 'POST',
              url: '/process_audio',
              data: form, // Our pretty new form
              processData: false, // tell jQuery not to process the data
              contentType: false // tell jQuery not to set contentType
            }).done(function(transcription) 
            {
                document.getElementById("output_text").innerHTML = "";
                console.log("Received transcript:"+transcription);
                $.post("/get_response", {"input_text_nm": transcription})
                .done(function(data) 
                {
                    response(data.message, data.sprite, data.sound, data.new_name);
                })
                .fail(function() 
                {
                    $("#output_text").html("An error has occurred.");
                });
            });
        }
      })
  
      // If any error occurs then handles the error 
      .catch(function (err) {
        console.log(err.name, err.message);
      });

    function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
      }

    async function typesplit(chunks)
    {
        for (var i=0; i<chunks.length;i++)
        {
            count = 0;
            text = chunks[i];
            affect_outputbox_css(text.length);
            for (let i=0; i<text.length; i++)
            {
                $("#output_text").append(character(count, count+1, text));
                count++;
                await sleep(30);
            }
            //console.log(chunks[i]);  
            await sleep(500); 
            //console.log(chunks[i]);
            //console.log(chunks.length);
            if( i != chunks.length-1)
            {
                $("#output_text").html("");
            }
        }
    }

    async function typeit(punch)
    {
        count = 0;
        text = punch;
        affect_outputbox_css(text.length);
        for (let i=0; i<text.length; i++)
        {
            $("#output_text").append(character(count, count+1, text));
            count++;
            await sleep(30);
        }
    }

    function character(start,end,text)
    {
        return text.substring(start,end);
    }

    function affect_outputbox_css(textlen)
    {
        switch (true)
        {
            case (textlen < 52):
                $("#output_text").css('top', '916px')
                break
            case (textlen < 90):
                $("#output_text").css('top', '881px')
                break
            case (textlen > 90):
                $("#output_text").css('top', '856px')
                break
        }   
    }
    
    function response(message, sprite, sound, new_name)
    {
        document.getElementById("output_text").innerHTML = "";
        document.getElementById("input_text").blur();
        if(message.length > 140)
        {
            var chunks = message.match(/.{1,140}(\s|$)/g);
            typesplit(chunks);
        }
        else
        {
            typeit(message);
        }
        
        $("#chihiro_sprite").attr({src: sprite});
        audioElement.setAttribute('src', sound);
        audioElement.play();
        if(new_name === 'second')
        {
            $.get("/second_response", $(this).serialize())
            .done(function(data) 
            {
                $("#output_text").html("");
                typeit(data.message);
                $("#label_user").html(data.new_name);
                $("#chihiro_sprite").attr({src: data.sprite});
                audioElement.setAttribute('src', data.sound);
                audioElement.play();
            })
            .fail(function() 
            {
                $("#output_text").html("An error has occurred.");
            });
        }
    }

    window.addEventListener("load", function() 
    {         
        $.get("/welcome", $(this).serialize()).done(function(data) 
        {
            async function waitfortransition()
            {
                await sleep(2000);
                typeit(data.message);
                $("#chihiro_sprite").attr({src: data.sprite});
                audioElement.setAttribute('src', data.sound);
                audioElement.play();
    
                if(data.new_name === 'second')
                {
                    
                    $.get("/second_response", $(this).serialize())
                    .done(function(data) 
                    {
                        async function sleepywelcome()
                        {
                            await sleep(5000);
                            $("#output_text").html("");
                            typeit(data.message);
                            $("#chihiro_sprite").attr({src: data.sprite});
                            audioElement.setAttribute('src', data.sound);
                            audioElement.play();
                        }
                        sleepywelcome();
                    })
                    .fail(function() 
                    {
                        $("#output_text").html("An error has occurred.");
                    });
                }
            }
            waitfortransition();
        });
    });

    $("form[name='input_form']").submit(function(event) 
    {
        if(document.getElementById("input_text").value == "")
        {
            return false;
        }
        else
        {
            event.preventDefault();
            $.post("/get_response", $(this).serialize())
            .done(function(data) 
            {
                response(data.message, data.sprite, data.sound, data.new_name);
            })
            .fail(function() 
            {
                $("#output_text").html("An error has occurred.");
            });
        }
    });
});

document.addEventListener("keyup", function(event) 
{
    if (event.keyCode === 13) 
    {
        if (document.getElementById("input_text").value.length !== 0)
        {
            document.getElementById("label_alter_ego").style.visibility = "visible";
            document.getElementById("label_user").style.visibility = "hidden";
            document.getElementById("input_text").value = "";
            document.getElementById("input_text").style.visibility = "hidden";
        }
        else
        {
            document.getElementById("output_text").innerHTML = "";
            document.getElementById("input_text").value = "";
            document.getElementById("label_alter_ego").style.visibility = "hidden";
            document.getElementById("label_user").style.visibility = "visible";
            document.getElementById("input_text").style.visibility = "visible";
            document.getElementById("input_text").focus();
        }
    }
});

// wait for images to be downloaded and start the animation
$(window).on('load', () => {
    requestAnimationFrame(step);
  });