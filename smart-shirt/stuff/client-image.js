/* Or use this example tcp client written in node.js.  (Originated with 
example code from 
http://www.hacksparrow.com/tcp-socket-programming-in-node-js.html.) */

var net = require('net');
var base64Img = require('base64-img');

var client = new net.Socket();

client.connect(8888, '127.0.0.1', function() {
    console.log('Connected to server !');
    process.stdout.write("message: ");
    base64Img.base64('images/shirt15.jpg', function(err, data) {
        client.write(data);
        // client.write('/r');
    })
    
});

client.on('data', function(data) {
	console.log('Received: ' + data);
	// client.end(); // kill client after server's response
});

client.on('close', function() {
	console.log('Connection closed');
});

var stdin = process.openStdin();

stdin.addListener("data", function(d) {
    // note:  d is an object, and when converted to a string it will
    // end with a linefeed.  so we (rather crudely) account for that  
    // with toString() and then trim() 
    str = d.toString().trim();
    // console.log("you entered: [" + str + "]");
    var s = {
                'name': 'client-json.js',
                'message': str
            };
    ss = JSON.stringify(s)
    console.log(ss)
    client.write(ss);
    process.stdout.write("message: ");
});