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
            // $('#imageSrc').attr('src', e.target.result);
            console.log(e.target.result);
            $("#imageSrc").css('background-image','url('+e.target.result+')');
            // Swtich mode from use camera to choose img from folder
            $(".choose-camera").removeClass("selected");
            $(".choose-img").addClass("selected");  
        }
        reader.readAsDataURL(input.files[0]);
    }
}

$("#fileInput").change(function() {
    readURL(this);
});

$(".choose-camera").click(function() {
    // Swtich mode from choose img from folder to use camera
    $(".choose-img").removeClass("selected");
    $(".choose-camera").addClass("selected");  
});

});
