var app = require('express')();
var http = require('http').Server(app);
var io = require('socket.io')(http);

http.listen(8080, function(){
	console.log('listening on *:8080');
});


app.get('/', function (req, res) {
	res.sendFile(__dirname + '/public/index.html');
});

setInterval( function() {
	var msg = Math.random();
	io.emit('message',msg);
	console.log(msg);
}, 1000);

/*
io.sockets.on('connection', function(socket) {
	var lightvalue = 0;
	socket.on('light', function(data) {
		lightvalue = data;
		if (lightvalue) {
			console.log(lightvalue);
		}
	});
});
*/
