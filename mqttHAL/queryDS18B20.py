#!/usr/bin/python
#queryDS18B20.py


def gettemp(sensor_id):
    try:
        mytemp = ''
        filename = 'w1_slave'
        f = open('/sys/bus/w1/devices/' + sensor_id + '/' + filename, 'r')
        line = f.readline()  # read 1st line
        crc = line.rsplit(' ', 1)
        crc = crc[1].replace('\n', '')
        if crc == 'YES':
            line = f.readline()  # read 2nd line
            mytemp = line.rsplit('t=', 1)
        else:
            mytemp = 99999
        f.close()
        return int(mytemp[1]) / float(1000)

    except:
        return 99999

if __name__ == '__main__':

    # Script has been called directly
    sensor_id = '28-0000072947c9'
    print "Temp : " + '{:.3f}'.format(gettemp(sensor_id))
