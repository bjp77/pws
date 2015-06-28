import serialenum
import serial

class DavisConsole(object):
    def __init__(self, conn):
        print "I'm a davis console"
    
    @staticmethod
    def discover():
	"""Return tuple with discovered serial connection."""
        return ('/dev/ttyS0', 19200, 1, serial.PARITY_NONE, 0)

    @property
    def measurement(self):
       """Return dictionary of measured values."""
       return {'Temperature':45, 'Humidity': 45}



   
