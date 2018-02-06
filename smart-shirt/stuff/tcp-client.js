/* Or use this example tcp client written in node.js.  (Originated with 
example code from 
http://www.hacksparrow.com/tcp-socket-programming-in-node-js.html.) */

var net = require('net');

var client = new net.Socket();
client.connect(8888, '127.0.0.1', function() {
    console.log('Connected to server !');
    process.stdout.write("message: ");
	client.write('Hello, server! Love, Client.');
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
    client.write(str);
    process.stdout.write("message: ");
});