import serialenum
import serial
import random
import datetime
import time
from requests.structures import LookupDict
import re

_commands = {
    'test': 'TEST\n',
    'loop': 'LOOP 1\n',
}

commands = LookupDict(name='command_strings')
for name in _commands:
    setattr(commands, name, _commands[name])

_patterns = {
    'test': 'TEST',
    'loop': 'LOO',
}
patterns = LookupDict(name='patther_strings')
for name in _patterns:
    setattr(patterns, name, _patterns[name])

class DavisConsole(object):
    def __init__(self, conn):
        self.serial = serial.Serial(conn[0], conn[1])

    @classmethod
    def discover(cls):
	"""Return tuple with discovered serial connection."""
        for port in serialenum.enumerate():
            ser = serial.Serial(port, 19200)
            ser.write(commands.test)
            time.sleep(0.1)
            data = ser.read(ser.inWaiting())
            m = re.search(patterns.test, data)
            if m != None:
                return cls((port, 19200))
        return None


    def measure(self):
       """Return dictionary of measured values."""
       ts = datetime.datetime.utcnow()
       temperature = random.randrange(-45,110)
       humidity = random.randrange(10, 100)
       return {'Time':ts, 'Temperature':temperature, 'Humidity':humidity}



   
