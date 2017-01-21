#!/usr/bin/env python
#cortex.py

import sys, time, logging, urllib, cortexMngr, actionsThreading, json, pickle

# cortex.txt contains a single line of codes that populates the cortex variable
# cortex is a list of dictionaries containing all
# canned reactions to incoming messages
# (see cortexManager.py)


logger = logging.getLogger('mainLogger')


class Cortex():
    cortex = []
    URLfileName = ''
    FileName = ''
    # creates a dictionary with a single inhibitor with 10 seconds validity
    # inhibitors = {'BlockBogus': time.time() + 10}
    # creates a dictionary of the current active enabler
        # (enablers describe the world as seen by Hal)
    currentEnablers = {'Night': ['Yes', time.time() + 10]}

    def __init__(self, urlfilename, fileName):
        self.URLfileName = urlfilename
        self.FileName = fileName
        logger = logging.getLogger('mainLogger')
        if not(self.updateCortexFromFile()):
            if self.updateFileFromURL():
                if not(self.updateCortexFromFile()):
                    logger.warning('Exiting... cortex not found, url not found')
                    sys.exit(1)
            else:
                logger.warning('Exiting... no cortex file @ given URL')
                sys.exit(1)
        logger.info(cortexMngr.DictOrListToString(self.cortex))

    def updateFileFromURL(self):
        try:
            url = open(self.URLfileName, 'r').read()
            urllib.urlretrieve(url, self.FileName)
            return True
        except Exception:
            return False

    def updateCortexFromFile(self):
        try:
            # a changer avec une fonction json
            #tmpCortex = eval(open(self.FileName, 'r').read())
            with open(self.FileName) as data_file:
                for line in data_file:
                    tmpCortex = json.loads(line)
                    #tmpCortex = pickle.loads(line)
                    break
        except Exception:
                return False
        while len(self.cortex) > 0:
            self.cortex.pop()
        self.cortex.extend(tmpCortex)
        return True

    def testEnablingConditions(self, i):
        # test if currentEnablers check conditions required in Scenario #i
        # incoming MsgDict is of the type
        # {'param_A': ['>', 26],'param_B':['=','param_C']}
        # currentEnablers is of the type
        # {'param_A': [27, 1468179048.4], 'Night': ['Yes', 1468083316.2]}
        # where 1468179048.4 is the expiry time of 'param_A'
        # function returns True if
        #       all parameters are present in currentEnablers
        #   AND all parameters have valid expiry time
        #   AND all conditions return True
        incomingMsgDict = self.cortex[i]['Enablers']
        now = time.time()
        for ListElement in incomingMsgDict:
            if not(ListElement in self.currentEnablers):
                return ("'" + ListElement + "' not in Enablers'")
            if (now > self.currentEnablers[ListElement][1] and
                    self.currentEnablers[ListElement][1] != 0):
                return ("'" + ListElement + "' obsolete'")
            LeftOfEquation = self.currentEnablers[ListElement][0]
            if isinstance(incomingMsgDict[ListElement][1],
                    (int, long, float, complex)):
                RightOfEquation = incomingMsgDict[ListElement][1]
            else:
                compEnabler = incomingMsgDict[ListElement][1]
                if not(compEnabler in self.currentEnablers):
                    return ("'" + compEnabler + "' not in Enablers'")
                if (now > self.currentEnablers[compEnabler][1] and
                        self.currentEnablers[compEnabler][1] != 0):
                    return ("'" + compEnabler + "' obsolete'")
                RightOfEquation = self.currentEnablers[compEnabler][0]
            if not cortexMngr.compare(LeftOfEquation, RightOfEquation,
                    incomingMsgDict[ListElement][0]):
                return('[' + str(LeftOfEquation) +
                    ' ' + incomingMsgDict[ListElement][0] + ' ' +
                    str(RightOfEquation) + '] not true!')
        return True

    def dispatchMsg2Action(self, incomingMsg):
        tmpEnablers = {}
        for key in self.currentEnablers:
            tmpEnablers[key] = self.currentEnablers[key][0]
        logger.info('______________________\ncortex.dispatchMsg2Action : ' +
            str(incomingMsg) + '\nEnablers : ' + str(tmpEnablers) +
            '\n_____________________________________________________________')
        reportOK = ''
        reportNOK = '\nScenarii not triggered: '
        actions = []
        incomingMsgDict = json.loads(incomingMsg)
        for i in range(len(self.cortex)):
            if cortexMngr.checkDict1FullyInDict2(
                    self.cortex[i]['IncomingMessage'], incomingMsgDict):
                reportOK = (reportOK + '\n' + 'Sc.' + str(i)
                    + " -->   1/2 Msg ok")
                test = self.testEnablingConditions(i)
                if test == True:
                    reportOK = reportOK + " | 2/2 Enablers ok"
                    for j in range(len(self.cortex[i]['ActionsSequence'])):
                        reportOK = (reportOK + "\n=======> " +
                        self.cortex[i]['ActionsSequence'][j]['Action']
                        + '  :  ' + str(self.cortex[i]
                        ['ActionsSequence'][j]['Arguments']))
                    actions.append(self.cortex[i]['ActionsSequence'])
                else:
                    reportOK = reportOK + " | 2/2 Enablers nok " + test
            else:
                reportNOK = reportNOK + 'Sc.' + str(i) + '; '
        logger.info('####################' + reportNOK + reportOK
            + '\n############################################################')
        return actions
