
//var fs = require('fs');
//var https = require('https');

/*var io = require('socket.io')(http);

https.listen(8080, function(){
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
*/
const WebSocket = require('ws');
const https = require('https');

//const server = new https.createServer({

const wss = new WebSocket.Server({port: 8080});

function lookupBarcode(upc) {
	https.get('https://api.upcitemdb.com/prod/trial/lookup?upc=' + upc, (resp) => {
		let data = "";
		resp.on('data', (chunk) => {
			data += chunk;
		});

		resp.on('end', () => {
			console.log(data);
			try {
				barcodeData = JSON.parse(data);
				console.log(barcodeData.items[0].title);
			} catch (err) {
				console.log(err.message);
			}
		});
	}).on("error", (err) => {
		console.log("Error: " + err.message);
	});
}

function handleEvt(evt) {
	switch(evt.type) {
		case "BARCODE_SCANNED":
			lookupBarcode(evt.value);
			break;
	}
}

wss.on('connection', function connection(ws) {
	ws.on('message', function incoming(message) {
		console.log('received: %s', message);
		evt = JSON.parse(message);
		handleEvt(evt);
	});
	/*setInterval( function() {
		var msg = Math.random();
		ws.send(msg);
		console.log('sent: %s', msg);
	});*/
});
/*
setInterval( function() {
	var msg = Math.random();
	ws.send(msg);
	console.log('sent: %s', msg);
});
*/
