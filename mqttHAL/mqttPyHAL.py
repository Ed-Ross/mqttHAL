#!/usr/bin/env python
#mqttPyHAL.py

import sys, time, logging, urllib
import cortexMngr, actionsThreading, cortex, json, threading
import paho.mqtt as mqtt

#note install with
#sudo apt-get install mosquitto
# AND
#sudo pip install paho-mqtt


class myLoop (threading.Thread):
    def __init__(self, client):
        threading.Thread.__init__(self)
        self.client = client

    def run(self):
        self.client.loop_forever()

if __name__ == "__main__":
    # create logger
#    logging.basicConfig(filename='example.log',level=logging.DEBUG)
    logger = logging.getLogger('mainLogger')
    logger.setLevel(logging.DEBUG)
    # create console handler and set level to debug
    rootPath = sys.path[0]
    ch = logging.FileHandler(filename=rootPath + '/myLogger.log')
    ch.setLevel(logging.DEBUG)
    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(filename)s - %(levelname)s - %(message)s')
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(ch)
    logger.info('####################################################')
    logger.info('##################STARTING##########################')
    logger.info('####################################################\n')
    cortexURLFileName = rootPath + '/config/cortexURL.ini'
    cortexFileName = rootPath + '/config/cortex.txt'
    Cortex = cortex.Cortex(cortexURLFileName, cortexFileName)

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(client, userdata, flags, rc):
        logger.info("Connected with result code " + str(rc))

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe("mqtt/HAL")

    # The callback for when a PUBLISH message is received from the server.
    def on_message(client, userdata, msg):
        sequenceSeries = Cortex.dispatchMsg2Action(msg.payload)
        for actionSequence in sequenceSeries:
            yalla1 = actionsThreading.actionsThreading(actionSequence, Cortex)
            yalla1.start()
    client = mqtt.client.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(host="localhost", port=1883, keepalive=60, bind_address="")
    a = myLoop(client)
    a.start()
    time.sleep(1)
    mqtt.publish.single("mqtt/HAL", json.dumps({'command': 'startup'}))
