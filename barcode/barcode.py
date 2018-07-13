import websocket
import fileinput
import json
import ssl

ws = websocket.create_connection("ws://localhost:8090");
#ws = websocket.create_connection("wss://localhost:8080", sslopt={"cert_reqs": ssl.CERT_NONE})

for line in fileinput.input():
    try:
        ws.send(json.dumps({"type":"BARCODE_SCANNED","value":line.replace("\n","")}))
    except (KeyboardInterrupt, SystemExit):
        ws.close();
        sys.exit(0);
