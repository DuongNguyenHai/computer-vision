const express = require('express');
const bodyParser = require('body-parser');
const app = express()

app.use(express.static('public'));
// app.use(express.static('resource'));
app.use(bodyParser.urlencoded({ extended: true }));
app.set('view engine', 'ejs');

const port = 3000;

app.get('/', function(req, res){
    res.render('index');
})

app.listen(3000, function(req, res){
    console.log('server is opening on port ' + port)
})
