#!/bin/bash

while true
do
	read -p "Input barcode: " code
	curl "https://api.upcitemdb.com/prod/trial/lookup?upc=$code" 2>/dev/null > response.txt
	cat response.txt
	echo ''
	jq '.items[0].title' < response.txt
	echo ""
done
