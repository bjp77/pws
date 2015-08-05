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

    class _data_desc(object):
        def __init__(self, offsets, divisor):
            assert(divisor > 0)
            self._offsets = offsets
            self._divisor = divisor

        def __call__(self, data):
            value = 0
            shift = 0

            for offset in self._offsets:
                value += data[offset] << shift
                shift += 8

            return float(value) / self._divisor

    _data_lookup = {
        'Temperature': _data_desc([13, 14], 10),
        'Humidity': _data_desc([34], 1),
        'Dewpoint': _data_desc([31, 32], 1),
        'Pressure': _data_desc([8, 9], 1000),
        'RainRate': _data_desc([42, 43], 100),
        'DailyRain': _data_desc([51, 52], 100),
        'WindSpeed': _data_desc([15], 1),
        'WindDir': _data_desc([17, 18], 1),
        'WindGustSpeed': _data_desc([23, 24], 10),
        'WindGustDir': _data_desc([25, 26], 1),
    }

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
       for key in self._data_lookup:
           try:
               obs[key] = self._data_lookup[key](dat_array)
           except (IndexError, KeyError) as e:
               logging.error(e)

       return obs
   
