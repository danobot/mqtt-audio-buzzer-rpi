import argparse
import signal
import sys
import time
import logging
import atexit
import paho.mqtt.client as mqtt
from RPi import GPIO



logging.basicConfig(level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S',
                    format='%(asctime)-15s - [%(levelname)s] buzzer: %(message)s', )

parser = argparse.ArgumentParser(description='Receives a decimal code via a 433/315MHz GPIO device')
parser.add_argument('-g', dest='pin',       type=int,   default=18,            help="GPIO pin (Default: 18)")
parser.add_argument('-d', dest="delay",     type=int,   default=0.05,          help="Buzz Length")
parser.add_argument('-p', dest="pause",     type=int,   default=0.5,            help="Pause Length")
parser.add_argument('-r', dest="reps",type=int,default=1, help="Buzzer Repetitions")
parser.add_argument('-c', dest="count",type=int,default=1, help="Buzzer Count (per repetition)")
parser.add_argument('--topic', dest="mqtt_topic",type=str,default='#', help="MQTT Topic to Listen to (Default: '#')")
parser.add_argument('--host', dest="mqtt_host",type=str,default='10.1.1.130', help="MQTT Host (Default: '10.1.1.130')")

args = parser.parse_args()

BUZZER_REPETITIONS = args.reps
BUZZER_COUNT = args.count
BUZZER_DELAY = args.delay
PAUSE_TIME = args.pause

PIN = args.pin
MQTT_TOPIC = args.mqtt_topic
MQTT_HOST = args.mqtt_host
logging.info("Buzzer connected on " + str(args.pin))
logging.info("MQTT Host: " + str(args.mqtt_host))
logging.info("MQTT Topic: " + str(args.mqtt_topic))


client = mqtt.Client()


client.connect(MQTT_HOST, 1883, 60)


GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN, GPIO.OUT)
GPIO.output(PIN, False)

timestamp = None

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(MQTT_TOPIC)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    buzz();

def buzz():
    for _ in range(BUZZER_REPETITIONS):
        logging.info("Buzzed!")
        # Beep BUZZER_COUNT TIMES
        for _ in range(BUZZER_COUNT):
            # Turn on then off
            for value in [True, False]:
                GPIO.output(PIN, value)
                time.sleep(BUZZER_DELAY)


client.on_connect = on_connect
client.on_message = on_message



# For clean exits
def exithandler(signal, frame):
    logging.info("Cleaning up")
    GPIO.output(PIN, False)
    GPIO.cleanup()
    client.disconnect()
    sys.exit(0)

import atexit
atexit.register(exithandler)
client.loop_forever()
