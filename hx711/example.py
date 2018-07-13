import RPi.GPIO as GPIO
import time
import sys
import websocket
import json
try:
        import thread
except ImportError:
        import _thread as thread
import time
from hx711 import HX711
from enum import Enum
import ssl

def on_message(ws, message):
    print(message)

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("WEBSOCKET CONNECTION CLOSED")

def on_open(ws):
    print("WEBSOCKET CONNECTION OPENED")

ws = websocket.create_connection("ws://localhost:8090");
#ws = websocket.create_connection("wss://localhost:8080", sslopt={"cert_reqs": ssl.CERT_NONE});
#ws.on_open = on_open
#ws.run_forever()

class State(Enum):
    MEASURE = 1
    STABLE = 2

def cleanAndExit():
    GPIO.cleanup()
    ws.close();
    sys.exit()

hx = HX711(5, 6)

hx.set_reading_format("LSB", "MSB")

hx.set_reference_unit(-23.4)

hx.reset()
hx.tare()

prev_val = 0
alpha = 0.2
val = 0
beta = 1 - alpha

stability_num = 5

state = State.STABLE
values = []
stable_val = 0

while True:
    try:
        prev_val = val
        val = alpha * prev_val + beta * hx.get_weight(1)
        #prev_val = val
        #print val
        #print round(val/10)*10

        hx.power_down()
        hx.power_up()
        #time.sleep(0.5)

        if state == State.MEASURE:
            if(len(values) >= stability_num):
                values.pop(0)
            values.append(val)
            if(len(values) >= stability_num):
                state = State.STABLE
                for v in values:
                    if abs(v - val) > 20:
                        state = State.MEASURE
            if state == State.STABLE:
                roundedVal = ((val - stable_val)/10)*10
                if abs(roundedVal) > 10:
                    ws.send(json.dumps({"type": "WEIGHT_CHANGED","value": roundedVal}));
                stable_val = val
        elif state == State.STABLE:
            if abs(prev_val - val) > 20:
                state = State.MEASURE
            else:
                stable_val = val


    except (KeyboardInterrupt, SystemExit):
        cleanAndExit()
