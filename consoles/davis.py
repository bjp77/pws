import serialenum
import serial
import random
import datetime

class DavisConsole(object):
    def __init__(self, conn):
        print "I'm a davis console"

    @staticmethod
    def discover():
	"""Return tuple with discovered serial connection."""
        return ('/dev/ttyS0', 19200, 1, serial.PARITY_NONE, 0)

    def measure(self):
       """Return dictionary of measured values."""
       ts = datetime.datetime.utcnow()
       temperature = random.randrange(-45,110)
       humidity = random.randrange(10, 100)
       return {'Time':ts, 'Temperature':temperature, 'Humidity':humidity}



   
