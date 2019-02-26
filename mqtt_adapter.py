#!/usr/bin/env python

import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--server', default = 'phobos', help = 'What MQTT server to connect to')
parser.add_argument('-p', '--port', default = 1883, help = 'What MQTT port to connect to')
parser.add_argument('-v', '--verbose', help = 'verbose output', action = 'store_true')
parser.add_argument('-t', '--topic', default = 'tele/sonoff/RESULT/#', help = 'What MQTT topic to listen to') 

args = parser.parse_args()

topic = "tele/sonoff/RESULT/#"

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(topic)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    m_decode = str(msg.payload.decode('utf-8', 'ignore'))

    try:
        msg_json = json.loads(m_decode)
    except Exception as e:
        print ('Exception: ', e)

    # Verify message to at least some extent
    if 'RfRaw' in msg_json:
        if msg_json['RfRaw']['Data'][0:4] == "AAA4" and msg_json['RfRaw']['Data'][22:24] == "55":
            publish.single("tele/sonoff/rf_message", msg_json['RfRaw']['Data'][16:22], hostname = args.server)

    if 'RfReceived' in msg_json:
        publish.single('tele/sonoff/rf_message', msg_json['RfReceived']['Data'], hostname = args.server) 


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(args.server, args.port, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
