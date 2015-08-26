from utils import DotDict
import sys
import logging

class _ObsValid():
    def __init__(self, min, max):
        self.min = min
        self.max = max

    def __call__(self, value):
        if value < self.min or value > self.max:
            raise ValueError('{0} is out of range'.format(value))

class _ObsData(DotDict):
    _valid = {
         'temperature': _ObsValid(-100, 150),
         'humidity': _ObsValid(0, 100),
         'pressure': _ObsValid(20, 32.5),
         'rain_rate': _ObsValid(0, 10.0),
         'daily_rain': _ObsValid(0, 10.0),
         'wind_speed': _ObsValid(0, 200),
         'wind_dir': _ObsValid(0, 360),
         'dewpoint': _ObsValid(-100, 150),
    }

    def __init__(self, data):
        for key in data:
            self.__setitem__(key, data[key])

    def __setattr__(self, name, value):
        try:
            self.__class__._valid[name](value)
            super(self.__class__, self).__setattr__(name, value)
        except (KeyError, ValueError) as e:
            logging.error(e)

    def __setitem__(self, key, value):
        try:
            self.__class__._valid[key](value)
            super(self.__class__, self).__setitem__(key, value)
        except (KeyError, ValueError) as e:
            logging.error(e)

class Observation(object):
    def __init__(self, stamp, data, maxes=[]):
        self.timestamp = stamp
        self.__maxes = dict(zip(maxes, [sys.float_info.min] * len(maxes)))
        self.data = data
        self.__count = 1

    @staticmethod
    def __make_max_key(key):
        return 'max_{0}'.format(key)

    @property
    def maxes(self):
        return self.__maxes

    @property
    def count(self):
        return self.__count

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = _ObsData(data)

        #First remove mexes that are not present in the data
        for missing_key in set(self.__maxes).difference(self._data):
            self.__maxes.pop(missing_key, None)

        #Now fill in maxes from the new data.
        for key in self.__maxes:
            self.__maxes[key] = self._data[key]

        self.__count = 1

    def update(self, data):
        update_data = _ObsData(data)
        self.__count += 1

        #First remove maxes that are not present in the update
        for missing_key in set(self.__maxes).difference(update_data):
            self.__maxes.pop(missing_key, None)

        #Now remote data that are not present in the update
        for missing_key in set(self._data).difference(update_data):
            self._data.pop(missing_key, None)

        #Now iterate over the data and compute a new weighted average
        new_weight = 1.0 / float(self.__count)
        old_weight = 1.0 - new_weight
        for key in self._data:
            #Compute weighted average
            self._data[key] = self._data[key] * old_weight +\
                              update_data[key] * new_weight
            #Check to see if we have found a new maximum
            if self.__maxes.has_key(key) and self.__maxes[key] < data[key]:
                self.__maxes[key] = data[key]

    def as_dict(self):
        data = {
            'time_stamp': self.timestamp
        }
        for key in self.__maxes:
            data[self.__make_max_key(key)] = self.__maxes[key]
        data.update(self._data)
        return data

