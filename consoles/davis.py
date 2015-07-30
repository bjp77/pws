import serialenum
import serial
import random
import datetime
import time
import re
import logging

class _Command(object):
    def __init__(self, cmd, patt):
        self.cmd = cmd
        self.patt = patt

class _lookup(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__

_command_map = {
    'test': _Command('TEST\n', '\x06TEST'),
    'loop': _Command('LPS 0x2 1\n', '\x06LOO'),
}

_commands = _lookup(_command_map)

class _SerialCommand(serial.Serial):
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
    '''Davis Vantage Pro2/Vue plugin class.'''

    #LOOP data offsets for various measurements.
    TEMP_HIGH = 14
    TEMP_LOW = 13
    HUMIDITY = 34
    PRESSURE_HIGH = 9
    PRESSURE_LOW = 8
    RAINRATE_HIGH = 43
    RAINRATE_LOW = 42
    WINDSPEED = 15
    WINDDIR_HIGH = 18
    WINDDIR_LOW = 17
    WINDGUSTSPEED_HIGH = 24
    WINDGUSTSPEED_LOW = 23
    WINDGUSTDIR_HIGH = 26
    WINDGUSTDIR_LOW = 25
    DEWPOINT_HIGH = 32
    DEWPOINT_LOW = 31

    def __init__(self, conn):
        self._serial = _SerialCommand(conn[0], conn[1])
    
    @classmethod
    def discover(cls):
	"""Return tuple with discovered serial connection."""
        for port in serialenum.enumerate():
            ser = _SerialCommand(port, 19200)
            if ser.exec_cmd(_commands.test) is not None:
                return cls((port, 19200))

        return None
        
    def measure(self):
       """Return dictionary of measured values."""
       obs = {}
       ts = datetime.datetime.utcnow()
       obs['Time'] = ts

       dat_array = self._serial.exec_cmd(_commands.loop)
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

       try:
           pressure = float((dat_array[self.PRESSURE_HIGH] << 8) + \
               dat_array[self.PRESSURE_LOW]) / 1000
           obs['Pressure'] = pressure
       except IndexError as e:
           logging.error(e)

       try:
           rainrate = float((dat_array[self.RAINRATE_HIGH] << 8) + \
               dat_array[self.RAINRATE_LOW]) / 100
           obs['RainRate'] = rainrate
       except IndexError as e:
           logging.error(e)

       try:
           windspeed = dat_array[self.WINDSPEED]
           obs['WindSpeed'] = windspeed
       except IndexError as e:
           logging.error(e)

       try:
            winddir = (dat_array[self.WINDDIR_HIGH] << 8) +  \
               dat_array[self.WINDDIR_LOW]
            obs['WindDir'] = winddir
       except IndexError as e:
           logging.error(e)

       try:
            windgustspeed = float((dat_array[self.WINDGUSTSPEED_HIGH] << 8) +  \
               dat_array[self.WINDGUSTSPEED_LOW]) / 10
            obs['WindGustSpeed'] = windgustspeed
       except IndexError as e:
           logging.error(e)

       try:
            windgustdir = (dat_array[self.WINDGUSTDIR_HIGH] << 8) +  \
               dat_array[self.WINDGUSTDIR_LOW]
            obs['WindGustDir'] = windgustdir
       except IndexError as e:
           logging.error(e)

       try:
            dewpoint = (dat_array[self.DEWPOINT_HIGH] << 8) +  \
               dat_array[self.DEWPOINT_LOW]
            obs['Dewpoint'] = dewpoint
       except IndexError as e:
           logging.error(e)

       return obs
   
