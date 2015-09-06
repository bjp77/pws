from utils import DotDict
import sys
import logging

class _ObsValid():
    """
    Raise a value error if called with a value outside the defined range.
    """
    def __init__(self, min, max):
        self.min = min
        self.max = max

    def __call__(self, value):
        """
        Raise ValueError if data is invalid.
        """
        if value < self.min or value > self.max:
            raise ValueError('{0} is out of range'.format(value))

class _ObsData(DotDict):
    """
    Observation data class.

    This class inherits from DocDict for convenience.  Attributes can be
    accessed like dictionary values or like class attributes.  In addition,
    this class validates all attribute values before setting them.
    """

    #Table of valid ranges for all observation types.  This table also
    #serves to define the expected set of measurements
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
        """
        Initialize the observation based on the provided data.

        Note that the super().__init__ is not used.  Instead, call our
        own __setitem__ method so we can guarantee the data is valid.

        :param data: dictionary containing observed values.
        """
        for key in data:
            self.__setitem__(key, data[key])

    def __setattr__(self, name, value):
        """
        Set an attribute value after checking validity.

        :param name: attribute name
        :param value: desired attribute value
        :raises ValueError: if attribute value is invalid
        """
        try:
            self.__class__._valid[name](value)
            super(self.__class__, self).__setattr__(name, value)
        except (KeyError, ValueError) as e:
            logging.error(e)

    def __setitem__(self, key, value):
        """
        Set an attribute value after checking validity.

        :param name: attribute name
        :param value: desired attribute value
        :raises ValueError: if attribute value is invalid
        """
        try:
            self.__class__._valid[key](value)
            super(self.__class__, self).__setitem__(key, value)
        except (KeyError, ValueError) as e:
            logging.error(e)

class Observation(object):
    """
    Observation class

    The Observation class rolls up one or more discrete observations
    into one consolidated view of the data.  It can track maximum values
    for selected fields and averages measurements across all observations.

    This class exists so that measurements can be taken and recorded at a
    relatively high frequency without requiring emission at the same rate.
    """
    def __init__(self, stamp, data, maxes=[]):
        """
        Initialize an observation.

        :param stamp: datetime at which the data were observed.
        :param data: dictionary of measurements
        :param maxes: list of measurements for which maxes should be kept
        """
        self.timestamp = stamp
        self.__maxes = dict(zip(maxes, [sys.float_info.min] * len(maxes)))
        self.data = data
        self.__count = 1

    @staticmethod
    def __make_max_key(key):
        """Return max key for specified measurement key."""
        return 'max_{0}'.format(key)

    @property
    def maxes(self):
        """Return the list of tracked maximum value keys."""
        return self.__maxes

    @property
    def count(self):
        """Return the number of measurements rolled up into this observation."""
        return self.__count

    @property
    def data(self):
        """Return the measured data."""
        return self._data

    @data.setter
    def data(self, data):
        """
        Set the measured data.  This resets the entire state of the observation
        and overwrites all previous observations.
        """
        self._data = _ObsData(data)

        #First remove mexes that are not present in the data
        for missing_key in set(self.__maxes).difference(self._data):
            self.__maxes.pop(missing_key, None)

        #Now fill in maxes from the new data.
        for key in self.__maxes:
            self.__maxes[key] = self._data[key]

        self.__count = 1

    def update(self, data):
        """
        Update an observation with a new measurement.

        This method takes a new measurement and computes a new average for
        all measured values.  New maximum values for any keys that have had
        maxes registered will be recorded.  Any measurement keys that are
        missing from the new data will be deleted.

        :param data: new measurement data
        """
        update_data = _ObsData(data)
        self.__count += 1

        #First remove maxes that are not present in the update
        for missing_key in set(self.__maxes).difference(update_data):
            self.__maxes.pop(missing_key, None)

        #Now remove data that are not present in the update
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
        """
        Build the complete obseration dictionary.

        This method represents the observation as a dictionary that
        inclues the timestamp and maximum values.
        """
        data = {
            'time_stamp': self.timestamp
        }
        for key in self.__maxes:
            data[self.__make_max_key(key)] = self.__maxes[key]
        data.update(self._data)
        return data

