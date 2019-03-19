#!/bin/bash

ctrl_c() {
	echo "KILLING PROCESSES"
	sudo kill -15 $WEIGHT_PID > /dev/null 2>&1
	sudo kill $BARCODE_PID > /dev/null 2>&1
	sleep 3
	sudo kill $SERVER_PID > /dev/null 2>&1
}

SOURCE_DIR="/home/pi/FYDP/"

SERVER_DIR=${SOURCE_DIR}SubliMate-Backend/app/
npm start --prefix $SERVER_DIR &> server.log &
sleep 10
python ${SOURCE_DIR}SubliMate-Hardware/hx711/example.py &
sudo python ${SOURCE_DIR}SubliMate-Hardware/barcode/barcode.py &
