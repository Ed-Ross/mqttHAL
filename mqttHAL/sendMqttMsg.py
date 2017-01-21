#!/usr/bin/python

import paho.mqtt.publish as publish
import json,sys



cmd = sys.argv[1]
payload = {'command': cmd}
msg = json.dumps(payload)
print (msg)
publish.single("mqtt/HAL", msg)
