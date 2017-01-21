#cortexManager.py
#!/usr/bin/python

# MODULE CONTAINING ALL FUNCTIONS NECESSARY TO MANAGE INTERACTIONS BETWEEN
# CORTEX, ENABLERS, INHIBITORS

import time, urllib, math, calendar, logging, operator, json
# from actionsThreading import actionsThreading

logger = logging.getLogger('mainLogger')
# SPECIAL FUNCTION TO PRINT CORTEX TO SCREEN


def DictOrListToString(DicOrList, n=0, indent=4, debug=False):
    res = ""
    prefix = "_" * n * indent
    if len(DicOrList) == 0:
        res = res + "(Vide)"
    if type(DicOrList) == type({}):
        for j in DicOrList:
            if type(DicOrList[j]) == type({}) or type(DicOrList[j]) == type([]):
                res = res + prefix + str(j) + ": \n" + DictOrListToString(
                        DicOrList[j], n + 1, indent)
            else:
                res = res + prefix + str(j )+ ": " + str(DicOrList[j]) + "\n"
    elif type(DicOrList) == type([]):
        for j in range(len(DicOrList)):
            if type(DicOrList[j]) == type({}) or type(DicOrList[j]) == type([]):
                res = res + prefix + str(j) + ": \n" + DictOrListToString(
                    DicOrList[j], n + 1, indent)
            else:
                res = res + prefix + str(j) + ": " + str(DicOrList[j]) + "\n"
    else:
        res = res + prefix + str(DicOrList)
    return res


def xplMsg2Dict(msg):
    msgList = msg.splitlines()
    result = {}
    for element in msgList:
        if element.find("=") != -1:
            elementList = element.split("=")
            result[elementList[0]] = elementList[1]
    return result


def checkDict1FullyInDict2(dict1, dict2):
    exists = True
    for elt in dict1:
        if elt in dict2:
            exists = dict1[elt] == dict2[elt]
        else:
            exists = False
        if not(exists):
            break
    return exists


def checkDict1VsObsoletingDict2(dict1, dict2):
    allow = True
    now = time.time()
    for ListElement in dict1:
        if ListElement in dict2:
            allow = (now < dict2[ListElement][1])
    # else false ???
        if not(allow):
            break
    return allow


def night(myUTCTime=0, debug=False, nightIncrease=30):
    # for tests : night(calendar.timegm((2015,4,2,0,0,0,0 ,0 ,0)),True)
    if myUTCTime == 0:
        myUTCTime = time.time()
    myTimeTuple = time.gmtime(myUTCTime)
    myDateTuple = myTimeTuple[0:3] + (0, 0, 0, 0, 0, 0)
    myUTCDate = calendar.timegm(myDateTuple)
    pi = math.pi
    cos = math.cos
    EarliestDawn = 3.7333
    YearlyAmplitude = 3.9833
    EarliestDusk = 15.8500
    RefDateDawn = 1419811200.0
    RefDateDusk = 1450137600.0
    YearLength = 31553280.0
    dawn = EarliestDawn + YearlyAmplitude / 2.0 * (
        1 + cos(pi * (myUTCDate - RefDateDawn) / YearLength * 2.0)) + (
        nightIncrease * 60)
    dusk = EarliestDusk + YearlyAmplitude / 2 * (
        1 + cos(pi * (1 - (myUTCDate - RefDateDusk) / YearLength * 2))) - (
        nightIncrease * 60)
    dawnTuple = myDateTuple[0:3] + time.gmtime(dawn * 3600)[3:6] + (0, 0, 0)
    duskTuple = myDateTuple[0:3] + time.gmtime(dusk * 3600)[3:6] + (0, 0, 0)
    if debug:
        print('##########')
        print (myTimeTuple)
        print (myDateTuple)
        print (dawnTuple)
        print (duskTuple)
    if (dawnTuple < myTimeTuple and duskTuple > myTimeTuple):
        return 'No'
    else:
        return 'Yes'


def compare(a, b, func):
    mappings = {'>': operator.gt, '>=': operator.ge,
                '==': operator.eq, '<': operator.lt,
                '<=': operator.le, '!=': operator.ne}
    return mappings[func](a, b)


def checkCriteria(dict1, dict2):
    for ListElement in dict1:
        if ListElement in dict2:
            allow = compare(dict2[ListElement][0],
                dict1[ListElement][1], dict1[ListElement][0])
            if not(allow):
                return False
    return True