$(document).ready(function () {
const LENGTH = 2;

$(".action").click(function() {
    var act = $(this).attr('action');
    $.ajax({
        url: '/action',
        type: 'GET',
        contentType: "application/json",
        data: {
            action: act
        },
        success: function(data) {
            console.log('action: ' + data);
        }
    });
})

var socket = io();
socket.on('measurement', function(msg) {
    var data = JSON.parse(msg);
    // console.log(data);
    for(dt in data) {
        if(dt!='type') {
            console.log(dt + ": " + data[dt][LENGTH]);
            length = data[dt][LENGTH];
            $(".tb-property-value[length="+ dt +"").text(length);
        }
    }
});

// User action

// select image to measure
// $("#fileInput").change(function(event) {
//     // var output = document.getElementById('imageSrc');
//     // output.src = URL.createObjectURL(event.target.files[0]);
//     console.log('url('+event.target.files[0]+')');
//     $(".camera-box ").css('background-image','url('+event.target.files[0]+')');
// })

function readURL(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function(e) {
            $("#imageSrc").css('background-image','url('+e.target.result+')');
            // Swtich mode from use camera to choose img from folder
            $(".choose-camera").removeClass("selected");
            $(".choose-img").addClass("selected");  
        }
        reader.readAsDataURL(input.files[0]);
    }
}

$(".choose-camera").click(function() {
    // Swtich mode from choose img from folder to use camera
    $(".choose-img").removeClass("selected");
    $(".choose-camera").addClass("selected");  
});

// upload image file

$('#upload-input').on('change', function(){
    readURL(this);
    var files = $(this).get(0).files;

    if (files.length > 0) {
        // create a FormData object which will be sent as the data payload in the
        // AJAX request
        var formData = new FormData();

        // loop through all the selected files and add them to the formData object
        for (var i = 0; i < files.length; i++) {
            var file = files[i];

            // add the files to formData object for the data payload
            formData.append('uploads[]', file, file.name);
        }

        $.ajax({
            url: '/upload',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(data) {
                // console.log('upload successful!\n' + data);
            }
            // xhr: function() {
            //     // create an XMLHttpRequest
            //     var xhr = new XMLHttpRequest();
            //     // listen to the 'progress' event
            //     xhr.upload.addEventListener('progress', function(evt) {
            //         if (evt.lengthComputable) {
            //             // calculate the percentage of upload completed
            //             var percentComplete = evt.loaded / evt.total;
            //             percentComplete = parseInt(percentComplete * 100);

            //             // update the Bootstrap progress bar with the new percentage
            //             $('.progress-bar').text(percentComplete + '%');
            //             $('.progress-bar').width(percentComplete + '%');
            //             // once the upload reaches 100%, set the progress bar text to done
            //             if (percentComplete === 100) {
            //                 $('.progress-bar').html('Done');
            //             }

            //         }
            //     }, false);

            //     return xhr;
            // }
        });
    }
});

});
