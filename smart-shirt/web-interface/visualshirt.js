var net = require('net');
const express = require('express');
const bodyParser = require('body-parser');
const app = express()
// socket io
var http = require('http').Server(app);
var io = require('socket.io')(http);

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
        // console.log(ss);
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

function showSizeOfShirt(data) {
    
}