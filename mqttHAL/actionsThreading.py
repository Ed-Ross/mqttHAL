#!/usr/bin/python
#actionsThreading.py

import threading, time, logging, re, json, queryDS18B20, RPi.GPIO as GPIO, sys
from cortexMngr import *
import paho.mqtt.publish as publish
import urllib2


class actionsThreading (threading.Thread):
    def __init__(self, actionsSequence, cortex):
        threading.Thread.__init__(self)
        self.actionsSequence = actionsSequence
        self.cortex = cortex

    def run(self):
        for action in self.actionsSequence:
            self.flexAction(action)

    def flexAction(self, action):
        logger = logging.getLogger('mainLogger')
        time.sleep(action['Tempo'])
        myRex = r"([^/]*)"
        radical = re.search(myRex, action['Action']).group(0)
        if radical == 'mqttmsg':
            publish.single("mqtt/HAL", json.dumps(action['Arguments']))
            #goXpl = xPLmessage()
            #goXpl.xplMsgGeneral(action['Action'][7:], action['Arguments'])
        elif radical == 'kill':
            sys.exit(1)
        elif radical == 'checkTmp':
            teta = queryDS18B20.gettemp(action['Arguments']['sensor'])
            self.cortex.currentEnablers[action['Arguments']['enabler']] = [teta,
                time.time() + float(action['Arguments']['duration'])]
        elif radical == 'inhibit':
            self.cortex.inhibitors[action['Arguments']['inhibitor']] = \
                time.time() + float(action['Arguments']['duration'])
        elif radical == 'setEnabler':
            if float(action['Arguments']['duration']) != 0:
                timeout = time.time() + float(action['Arguments']['duration'])
            else:
                timeout = 0
            self.cortex.currentEnablers[action['Arguments']['enablerName']] = \
                [action['Arguments']['enablerValue'], timeout]
        elif radical == 'updateEnablerBatchFromURL':
            try:
                response = urllib2.urlopen(action['Arguments']['URL'])
                myJson = json.loads(response.read())
                logger.info('\nmyJson:')
                logger.info(myJson)
                for item in myJson:
                    if float(item['duration']) != 0:
                        timeout = time.time() + float(item['duration'])
                    else:
                        timeout = 0
                    self.cortex.currentEnablers[item['enablerName']] = \
                        [item['enablerValue'], timeout]
            except Exception:
                logger.info('\n################# batch enablers: URL not found')
        elif radical == 'updateCortex':
            self.cortex.updateFileFromURL()
            self.cortex.updateCortexFromFile()
            logger.info('\n#################################\n######### ' +
                'UPDATED CORTEX ########\n#################################\n'
                + DictOrListToString(self.cortex.cortex, 0, 4, True))
        elif radical == 'switchOnOff':
            myPin = int(action['Arguments']['GPIO'])
            if action['Arguments']['State'] == 'TRUE':
                nextState = GPIO.HIGH
            else:
                nextState = GPIO.LOW
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(myPin, GPIO.OUT, initial=GPIO.HIGH)
            GPIO.output(myPin, nextState)
        elif radical == 'checkNight':
            logger.info('Enablers_before', self.cortex.currentEnablers)
            if(self.cortex.currentEnablers['Night'] != night()):
                self.cortex.currentEnablers['Night'] = night()
                logger.info('Enablers_after', self.currentEnablers)
        else:
            logger.info('\nAction not recognized')

