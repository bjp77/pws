from utils import DotDict
import logging

class Observation(object):
    class _ObsData(DotDict):
        class _ValidRange():
            def __init__(self, min, max):
                self.min = min
                self.max = max

            def __call__(self, val):
                return val >= self.min and val <= self.max

        _valid = {
            'temperature': _ValidRange(-100, 150),
            'humidity': _ValidRange(0, 100),
            'pressure': _ValidRange(20, 32.5),
            'rain_rate': _ValidRange(0, 10.0),
            'daily_rain': _ValidRange(0, 10.0),
            'wind_speed': _ValidRange(0, 200),
            'wind_dir': _ValidRange(0, 360),
            'dewpoint': _ValidRange(-100, 150),
        }

        def __init__(self, data):
            del_key_list = []
            for key in data:
                try:
                    if not self.__class__._valid[key](data[key]):
                        del_key_list.append(key)
                except KeyError:
                    logging.error('{0} value {1} is out of range' \
                                  .format(key,data[key]))
                    del_key_list.append(key)

            for key in del_key_list:
                data.pop(key, None)

            super(self.__class__, self).__init__(data)

        def __setattr__(self, name, value):
            if self.__class__._valid[name](value):
                super(self.__class__, self).__setattr__(name, value)

        def __setitem__(self, key, value):
            if self.__class__._valid[key](value):
                super(self.__class__, self).__setitem__(key, value)

    def __init__(self, stamp, data, maxes=[]):
        self.timestamp = stamp
        self._data = self.__class__._ObsData(data)
        self.__count = 1
        self.__maxes = self.__class__._ObsData({})
        for key in maxes:
            self.__maxes[key] = self._data[key]

    @staticmethod
    def __make_max_key(key):
        return 'max_{0}'.format(key)

    @property
    def maxes(self):
        return self.__maxes

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data, maxes=[]):
        self._data = self.__class__._ObsData(data)
        if len(maxes) > 0:
            self.__maxes = self.__class__._Obsdata({})
            for key in maxes:
                self.__maxes[key] = self._data[key]
        else:
            for key in self.__maxes:
                self.__maxes[key] = self._data[key]
        self.__count = 1

    def update(self, data):
        del_key_list = []
        self.__count +=1
        update_data = self.__class__._ObsData(data)
        for key in self._data:
            try:
                new_weight = 1.0 / float(self.__count)
                old_weight = 1.0 - float(new_weight)
                self._data[key] = self._data[key] * old_weight +\
                                  update_data[key] * new_weight
                if self.__maxes.has_key(key) and\
                   self.__maxes[key] < data[key]:
                        self.__maxes[key] = data[key]
            except KeyError:
                del_key_list.append(key)

        for key in del_key_list:
            self._data.pop(key, None)

    def as_dict(self):
        data = {
            'time_stamp': self.timestamp
        }
        for key in self.__maxes:
            data[self.__make_max_key(key)] = self.__maxes[key]
        data.update(self._data)
        return data

