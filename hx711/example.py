import RPi.GPIO as GPIO
import time
import signal
import sys
import websocket
import json

from argparse

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
    if output:
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

# Initialize the various parameters
parser = argparse.ArgumentParser()
parser.add_argument("-a", "--alpha", type=float, default=0.5 help="Alpha value to be used for exponential smoothing")
parser.add_option("-s", "--stability", type=int, default=10 help="Number of samples to use to determine stability")
parser.add_option("-t1", "--measure", type=int, default=10 help="Threshold used to determine when we transition to MEASURE state")
parser.add_option("-t2", "--change", type=int, default=50 help="Threshold used to determine what is considered a significant change")
parser.add_option("-t3", "--accuracy", type=int, default=5 help="The acceptable error range for measurements")
parser.add_option("-o", "--output", action="store_true", default=False help="Print output to a file. Useful for statistics gathering")
parser.add_option("-v", "--verbose", action="store_true", default=False help="Output each measurement to the console")
args = parser.parse_args()

alpha = args.alpha
stability_num = args.stability
threshold_1 = args.measure
threshold_2 = args.change
threshold_3 = args.accuracy
verbose = args.verbose
output = args.output

beta = 1 - alpha

# Initialize the system
val = 0
counter = 0
prev_val = 0
state = State.STABLE
values = []
stable_val = 0
start_time = 0

#Write timing and weight measurements to a file
if output:
    f = open("%f_%d_%d_%d_%d.csv" % (alpha, stability_num, threshold_1, threshold_2, threshold_3), "w")
    f.write("Weight Change Measured (g), Time taken to measure (s)\n")
print "Ready"

while True:
    try:
        prev_val = val
        weight = hx.get_weight(1)
        val = alpha * prev_val + beta * weight
        
        # Print measured value to the console
        if verbose:
            print val

        hx.power_down()
        hx.power_up()

        #populate the initial set of numbers
        if( len(values) < stability_num ):
            values.append(val)
            continue
        
        if state == State.MEASURE:
            #add the new value
            values.pop(0)
            values.append(val)
            
            #if any values are too far from our measurement continue measuring
            state = any( abs(v - val) > threshold_3 for v in values) ? State.MEASURE : State.STABLE

            if state == State.STABLE:
                #check if this change is large enough to qualify as an event
                if abs(val-stable_val) > threshold_2:
                    #printing portion
                    if output:
                        counter += 1
                        print "%d" % counter 
                        f.write("%f, %f\n" % (abs(roundedVal), time.time() - start_time))
                    ws.send(json.dumps({"type": "WEIGHT_CHANGED","value": roundedVal}));
                
                #Store the average value of values
                stable_val = sum(values)/len(values)
         
         elif state == State.STABLE:
            #if a change in values is large enough, begin measuring
            if abs(prev_val - val) > threshold_1:
                state = State.MEASURE
                start_time = time.time()
            else:
                stable_val = sum(values)/len(values)
    
    except KeyboardInterrupt, SystemExit:
        cleanAndExit()
