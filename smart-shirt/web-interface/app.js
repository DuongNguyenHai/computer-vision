var net = require('net');
const express = require('express');
const bodyParser = require('body-parser');
const app = express()
// socket io
var http = require('http').Server(app);
var io = require('socket.io')(http);
// upload file
var path = require('path');
var formidable = require('formidable');
var fs = require('fs');


// tcp/ip
var client = new net.Socket();
var port = process.env.PORT || 3000;


app.use(express.static('public'));
// app.use(express.static('resource'));
app.use(bodyParser.urlencoded({ extended: true }));
app.set('view engine', 'ejs');

app.get('/', function(req, res){
    res.render('index');
});

app.post('/', function(req, res){
    res.render('');
});

app.get('/action', function(req, res) {
    // console.log(req.query.action);
    if(req.query.action=="measure") {
        s = {action:'measure'};
        ss = JSON.stringify(s)
        client.write(ss);
    }
    res.sendStatus(200);
});

// app.listen(3000, function(req, res){
//     console.log('server is opening on port ' + port)
// });

http.listen(3000, function() {
    console.log('listening on *:' + 3000);
});

io.on('connection', function(socket){
    socket.on('chat message', function(msg){
        io.emit('chat message', msg);
    });
});

// client tcp/ip
client.connect(8888, '127.0.0.1', function() {
    console.log('Connected to server !');
});

client.on('data', function(data) {
    // console.log('Received: ' + data);
    js = JSON.parse(data)
    if(js.type=='measurement') {
        ss = JSON.stringify(js);
        // console.log(ss);
        io.emit('measurement', ss);
    }
});

client.on('close', function() {
	console.log('Connection closed');
});

app.post('/upload', function(req, res){

    // create an incoming form object
    var form = new formidable.IncomingForm();
  
    // specify that we want to allow the user to upload multiple files in a single request
    form.multiples = true;
  
    // store all uploads in the /uploads directory
    form.uploadDir = path.join(__dirname, '../uploads');
  
    // every time a file has been uploaded successfully,
    // rename it to it's orignal name
    form.on('file', function(field, file) {
        let ss = file.name;
        ss = ss.split('.');
        extensionFile = ss[1];
        fs.rename(file.path, path.join(form.uploadDir, 'shirt.'+extensionFile));
    });
  
    // log any errors that occur
    form.on('error', function(err) {
        console.log('An error has occured: \n' + err);
    });
  
    // once all the files have been uploaded, send a response to the client
    form.on('end', function() {
        res.end('success');
    });
  
    // parse the incoming request containing the form data
    form.parse(req);
  
  });