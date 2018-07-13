#!/bin/bash

ctrl_c() {
	echo "KILLING PROCESSES"
	kill $WEIGHT_PID > /dev/null 2>&1
	sleep 3
	kill $SERVER_PID > /dev/null 2>&1
}

SOURCE_DIR="/home/pi/FYDP/"

trap ctrl_c INT
SERVER_DIR=${SOURCE_DIR}SubliMate-Backend/app/
npm start --prefix $SERVER_DIR &
SERVER_PID=$!
sleep 3
python ${SOURCE_DIR}SubliMate-Hardware/hx711/example.py &
WEIGHT_PID=$!
python ${SOURCE_DIR}SubliMate-Hardware/barcode/barcode.py > /dev/null 2>&1

