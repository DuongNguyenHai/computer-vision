$(document).ready(function () {
const START = 0;
const END = 1;
const X = 0;
const Y = 1;
const LENGTH = 2;
var imgElement = document.getElementById("imageSrc");
var canvas = document.getElementById("canvasOutput");
const real_K = 0.12919132;
var points;

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
    points = JSON.parse(msg);
    console.log(points);
    for(dt in points) {
        if(dt!='type') {
            console.log(dt + ": " + points[dt][LENGTH]);
            length = (points[dt][LENGTH] * real_K).toFixed(2);
            $(".tb-property-value[length="+ dt +"").text(length);
        }
    }
    drawPoints(points);
});

function drawPoints(data) {
    showVericalLength(data, "bodyLength", "#f4c542");
    showVericalLength(data, "armHoleLength", "#4150f4", [4,0]);
    showHorizontalLength(data, "chestWidth", "#9b0000", [0, -10]);
    showHorizontalLength(data, "hemWidth", "#f4f442", [0, -10]);
    showHorizontalLength(data, "shoulderWidth", "#f4c441", [0, -10]);
    showLength(data, "sleeveHemWidth", "#42f450", [0,0]);
    showLength(data, "sleeveLength", "#f441d3", [10,15]);
}

function showVericalLength(data, type, color, adjust = [0,0]) {
    avx = data[type][START][X] + Math.round((data[type][END][X]-data[type][START][X])/2 + 0.5) + adjust[X];
    avy = data[type][START][Y] + Math.round((data[type][END][Y]-data[type][START][Y])/2 + 0.5) + adjust[Y];
    drawLine(canvas, [avx, data[type][START][Y]], [avx, data[type][END][Y]], color, 3);
    writeText(canvas, (data[type][LENGTH]*real_K).toFixed(2).toString(), color, [avx+10,avy]);
}

function showHorizontalLength(data, type, color, adjust=[]) {
    avx = data[type][START][X] + Math.round((data[type][END][X] - data[type][START][X])/2 + 0.5);
    if(data[type][END][Y]>=data[type][END][Y]) {
        avy = data[type][START][Y] + Math.round((data[type][END][Y] - data[type][START][Y])/2 + 0.5);
    }  
    else {
        avy = data[type][END][Y] + Math.round((data[type][START][Y] - data[type][END][Y])/2 + 0.5);
    }        
    drawLine(canvas, [data[type][START][X], avy], [data[type][END][X], avy], color, 3);
    writeText(canvas, (data[type][LENGTH]*real_K).toFixed(2).toString(), color, [avx+adjust[X],avy+adjust[Y]]);
}

function showLength(data, type, color, adjust = []) {
    avx = data[type][START][X] + Math.round((data[type][END][X]-data[type][START][X])/2 + 0.5);
    avy = data[type][START][Y] + Math.round((data[type][END][Y]-data[type][START][Y])/2 + 0.5);

    drawLine(canvas, data[type][START], data[type][END], color, 3);
    writeText(canvas, (data[type][LENGTH]*real_K).toFixed(2).toString(), color, [avx+adjust[X],avy+adjust[Y]]);
} 
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
            $('#imageSrc').attr('src', e.target.result);
            // $("#imageSrc").css('background-image','url('+e.target.result+')');
            // Swtich mode from use camera to choose img from folder
            $(".choose-camera").removeClass("selected");
            $(".choose-img").addClass("selected");

            // let imgElement = document.getElementById("imageSrc")
            // let mat = cv.imread(imgElement);
            // cv.imshow('canvasOutput', mat);
            
        }
        reader.readAsDataURL(input.files[0]);
    }
}

imgElement.onload = function() {
    let img = cv.imread(imgElement);
    cv.imshow('canvasOutput', img);
    img.delete();
};

function drawLine(cs, pointStart, pointStop, color, width) {
    var ctx = cs.getContext("2d");
    ctx.beginPath();
    ctx.moveTo(pointStart[0], pointStart[1]);
    ctx.lineTo(pointStop[0], pointStop[1]);
    ctx.strokeStyle = color;
    ctx.lineWidth = width;
    ctx.stroke();
}

function writeText(cs, str, color, pos) {
    var ctx = cs.getContext("2d");
    ctx.font = "25px Comic Sans MS";
    ctx.fillStyle = color;
    ctx.fillText(str, pos[0], pos[1]);

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
