import websocket
import fileinput
import json

ws = websocket.create_connection("ws://localhost:8080")

for line in fileinput.input():
    try:
        ws.send(json.dumps({"type":"BARCODE_SCANNED","value":line.replace("\n","")}))
    except (KeyboardInterrupt, SystemExit):
        ws.close();
        sys.exit(0);
