import RPi.GPIO as GPIO
import time
import signal
import sys
import websocket
import json
try:
        import thread
except ImportError:
        import _thread as thread
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

def cleanAndExit(signal, frame):
    print "Cleaning up..."
    f.close()
    GPIO.cleanup()
    ws.close()
    print "Done"
    sys.exit()

signal.signal(signal.SIGTERM, cleanAndExit)

hx = HX711(5, 6)

hx.set_reading_format("LSB", "MSB")

hx.set_reference_unit(-23.4)

hx.reset()
hx.tare()

counter = 0
prev_val = 0
alpha = 0.7
val = 0
beta = 1 - alpha

stability_num = 10
threshold_1 = 10
threshold_2 = 50
threshold_3 = 5

state = State.STABLE
values = []
stable_val = 0
start_time = 0
f = open("%f_%d_%d_%d_%d.csv" % (alpha, stability_num, threshold_1, threshold_2, threshold_3), "w")
f.write("Weight Change Measured (g), Time taken to measure (s)\n")
print "Ready"

while True:
    try:
        prev_val = val
        weight = hx.get_weight(1)
        val = alpha * prev_val + beta * weight
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
                    if abs(v - val) > threshold_3:
                        state = State.MEASURE
            if state == State.STABLE:
                roundedVal = ((val - stable_val)/10)*10
                if abs(roundedVal) > threshold_2:
                    counter += 1
                    print "%d" % counter 
                    f.write("%f, %f\n" % (abs(roundedVal), time.time() - start_time))
                    ws.send(json.dumps({"type": "WEIGHT_CHANGED","value": roundedVal}));
                    #print "WEIGHT_CHANGED"
                    #print time.time() - start_time
                    #print roundedVal

                stable_val = val
        elif state == State.STABLE:
            if abs(prev_val - val) > threshold_1:
                state = State.MEASURE
                start_time = time.time()
            else:
                stable_val = val
    except KeyboardInterrupt, SystemExit:
        cleanAndExit()
