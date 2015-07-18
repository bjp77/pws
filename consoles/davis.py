import serialenum
import serial
import random
import datetime
import time
import re

class Command(object):
    def __init__(self, cmd, patt):
        self.cmd = cmd
        self.patt = patt

class lookup(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__

_commands = {
    'test': Command('TEST\n', 'TEST'),
    'loop': Command('LOOP 1\n', 'LOO'),
}

commands = lookup(_commands)

class DavisConsole(object):
    TEMP_HIGH = 14
    TEMP_LOW = 13
    HUMIDITY = 34

    def __init__(self, conn):
        self.serial = serial.Serial(conn[0], conn[1])
    
    @classmethod
    def discover(cls):
	"""Return tuple with discovered serial connection."""
        for port in serialenum.enumerate():
            ser = serial.Serial(port, 19200)
            ser.write(commands.test.cmd)
            time.sleep(0.1)
            data = ser.read(ser.inWaiting())
            m = re.search(commands.test.patt, data)
            if m != None:
                return cls((port, 19200))

        return None

    def _exec_cmd(self, cmd):
        self.serial.write(cmd.cmd)
        time.sleep(0.1)
        data = self.serial.read(self.serial.inWaiting())
        if re.search(cmd.patt, data) is not None:
            return data, [ord(c) for c in data]
        else:
            return None, None
        
    def measure(self):
       """Return dictionary of measured values."""
       ts = datetime.datetime.utcnow()
       dat_string, dat_array = self._exec_cmd(commands.loop)
       temp = ((dat_array[self.TEMP_HIGH] << 8) + dat_array[self.TEMP_LOW]) / 10
       humidity = dat_array[self.HUMIDITY]
       return {'Time':ts, 'Temperature':temp, 'Humidity':humidity}
   
