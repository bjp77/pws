import serialenum
import serial
import random
import datetime
import time
import re
import logging

class Command(object):
    def __init__(self, cmd, patt):
        self.cmd = cmd
        self.patt = patt

class lookup(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__

_commands = {
    'test': Command('TEST\n', '\x06TEST'),
    'loop': Command('LOOP 1\n', '\x06LOO'),
}

commands = lookup(_commands)

class SerialCommand(serial.Serial):
    def exec_cmd(self, cmd):
        for attempt in range(1, 5):
            self.write(cmd.cmd)
            time.sleep(0.55555)
            data = self.read(self.inWaiting())
            if re.search(cmd.patt, data) is not None:
                return [ord(c) for c in data]
        else:
            return []

class DavisConsole(object):
    TEMP_HIGH = 14
    TEMP_LOW = 13
    HUMIDITY = 34

    def __init__(self, conn):
        self._serial = SerialCommand(conn[0], conn[1])
    
    @classmethod
    def discover(cls):
	"""Return tuple with discovered serial connection."""
        for port in serialenum.enumerate():
            ser = SerialCommand(port, 19200)
            if ser.exec_cmd(commands.test) is not None:
                return cls((port, 19200))

        return None
        
    def measure(self):
       """Return dictionary of measured values."""
       obs = {}
       ts = datetime.datetime.utcnow()
       obs['Time'] = ts

       dat_array = self._serial.exec_cmd(commands.loop)
       try:
            temp = float((dat_array[self.TEMP_HIGH] << 8) +  \
               dat_array[self.TEMP_LOW]) / 10
            obs['Temperature'] = temp
       except IndexError as e:
           logging.error(e)

       try:
           humidity = dat_array[self.HUMIDITY]
           obs['Humidity'] = humidity
       except IndexError as e:
           logging.error(e)

       return obs
   
