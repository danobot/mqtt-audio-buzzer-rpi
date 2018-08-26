import argparse
import signal
import sys
import os
import time
import logging
import atexit
import json
import paho.mqtt.client as mqtt
from RPi import GPIO



logging.basicConfig(level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S',
                    format='%(asctime)-15s - [%(levelname)s] buzzer: %(message)s', )

parser = argparse.ArgumentParser(description='Receives a decimal code via a 433/315MHz GPIO device')
parser.add_argument('-g', dest='pin',       type=int,   default=18,            help="GPIO pin (Default: 18)")
parser.add_argument('-r', dest="reps",type=int,default=1, help="Buzzer Repetitions")
parser.add_argument('-p', dest="pause",     type=int,   default=5,            help="Pause Length")
parser.add_argument('-d', dest="length",     type=int,   default=5,          help="Buzz Length")
parser.add_argument('-c', dest="count",type=int,default=1, help="Buzzer Count (per repetition)")
parser.add_argument('--topic', dest="mqtt_topic",type=str,default='-', help="MQTT Topic to Listen to (Default: '#')")
parser.add_argument('--host', dest="mqtt_host",type=str,default='10.1.1.130', help="MQTT Host (Default: '10.1.1.130')")
# parser.add_argument('--env', dest="env",default=False,const=True , action='store_const',help="Whether the script is configured using environment variables")

args = parser.parse_args()
default_options = args

MQTT_HOST = os.getenv('MQTT_HOST') if os.getenv('MQTT_HOST') else args.mqtt_host
MQTT_TOPIC = os.getenv('MQTT_TOPIC') if os.getenv('MQTT_TOPIC') else args.mqtt_topic
PIN = os.getenv('GPIO_PIN') if os.getenv('GPIO_PIN') else args.pin


default_options.reps = os.getenv('BUZZER_REPS') if os.getenv('BUZZER_REPS') else default_options.reps
default_options.pause = os.getenv('BUZZER_PAUSE') if os.getenv('BUZZER_PAUSE') else default_options.pause
default_options.length = os.getenv('BUZZER_LENGTH') if os.getenv('BUZZER_LENGTH') else default_options.length
default_options.count = os.getenv('BUZZER_COUNT') if os.getenv('BUZZER_COUNT') else default_options.count

logging.info("Buzzer connected on " + str(PIN))
logging.info("MQTT Host: " + str(MQTT_HOST))
logging.info("MQTT Topic: " + str(MQTT_TOPIC))

client = mqtt.Client()

client.connect(MQTT_HOST, 1883, 60)

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN, GPIO.OUT)
GPIO.output(PIN, False)

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    logging.info("Connected to MQTT broker with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(MQTT_TOPIC)
    client.subscribe(MQTT_TOPIC+"/short")
    client.subscribe(MQTT_TOPIC+"/long")
    client.subscribe(MQTT_TOPIC+"/alarm")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    topic = msg.topic
    split = topic.split("/")
    a = split[-1]

    if a == 'short':
        preset_short(client, userdata, msg)
    elif a == 'long':
        preset_long(client, userdata, msg)
    elif a == 'alarm':
        preset_alarm(client, userdata, msg)
    else:
        base(client, userdata, msg)


def base(client, userdata, msg):
    if msg.payload:
        #logging.debug("Payload" + str(msg.payload))
        options = parseJson(msg.payload)
        buzz(options)
    else:
        buzz(default_options)


def parseJson(payload):
    j = json.loads(payload)
    options = default_options # use defaults but overwrite if supplied
    if 'reps' in j:
        options.reps = j['reps']

    if 'pause' in j:
        options.pause = j['pause']

    if 'length' in j:
        options.length = j['length']

    if 'count' in j:
        options.count = j['count']

    return options


def buzz(options):
    logging.debug("Buzzed [reps=" + str(options.reps)
        + ", pause=" + str(options.pause)
        + ", length=" + str(options.length)
        + ", count=" + str(options.count) +"]")

    for _ in range(options.reps):
        # Beep `count` TIMES
        for _ in range(options.count):
            # Turn on then off
            for value in [True, False]:
                GPIO.output(PIN, value)
                # leave on for `length`
                time.sleep(options.length/100)

        time.sleep(options.pause)

# PRESETS
def preset_short(client, userdata, msg):
    options = default_options
    options.reps = 1
    options.pause = 1
    options.length = 20
    options.count = 1
    buzz(options)
def preset_long(client, userdata, msg):
    options = default_options
    options.reps = 1
    options.pause = 1
    options.length = 50
    options.count = 1
    buzz(options)
def preset_alarm(client, userdata, msg):
    options = default_options
    options.reps = 3
    options.pause = 0.6
    options.length = 6
    options.count = 3
    buzz(options)


# MQTT Subscriptions
# subscribe.callback(base, MQTT_TOPIC, hostname=MQTT_HOST)
# subscribe.callback(preset_short, MQTT_TOPIC+"/short", hostname=MQTT_HOST)
# subscribe.callback(preset_long, MQTT_TOPIC+"/long", hostname=MQTT_HOST)
# subscribe.callback(preset_alarm, MQTT_TOPIC+"/alarm", hostname=MQTT_HOST)
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
