#!/bin/bash

ctrl_c() {
	echo "KILLING PROCESSES"
	kill $WEIGHT_PID > /dev/null 2>&1
	sleep 3
	kill $SERVER_PID > /dev/null 2>&1
}

trap ctrl_c INT
node ~/SubliMate-Hardware/websocket/webserver.js &
SERVER_PID=$!
sleep 3
python ~/SubliMate-Hardware/hx711/example.py &
WEIGHT_PID=$!
python ~/SubliMate-Hardware/barcode/barcode.py > /dev/null 2>&1

