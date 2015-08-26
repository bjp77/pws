import unittest
from observer.observation import Observation
import datetime
import json

class ObserationTestBase(unittest.TestCase):
    @staticmethod
    def __get_item(source, key):
        return source[key]

    @staticmethod
    def __set_item(dest, key, value):
        dest[key] = value

    def test_add_valid_data(self):
        """Test adding valid measurements to observation."""
        ts = datetime.datetime.utcnow()
        data = {
            "temperature": 62.0,
            "humidity": 45.0,
            "dewpoint": 50.0,
            "pressure": 29.123,
            "rain_rate": 0.12,
            "daily_rain": 0.46,
            "wind_speed": 11.23,
            "wind_dir": 296.0
        }
        obs = Observation(ts, data)

        self.assertEqual(obs.data.temperature, 62.0)
        self.assertEqual(obs.data['temperature'], 62.0)

        self.assertEqual(obs.data.humidity, 45.0)
        self.assertEqual(obs.data['humidity'], 45.0)

        self.assertEqual(obs.data.dewpoint, 50.0)
        self.assertEqual(obs.data['dewpoint'], 50.0)

        self.assertEqual(obs.data.pressure, 29.123)
        self.assertEqual(obs.data['pressure'], 29.123)

        self.assertEqual(obs.data.rain_rate, 0.12)
        self.assertEqual(obs.data['rain_rate'], 0.12)

        self.assertEqual(obs.data.daily_rain, 0.46)
        self.assertEqual(obs.data['daily_rain'], 0.46)

        self.assertEqual(obs.data.wind_speed, 11.23)
        self.assertEqual(obs.data["wind_speed"], 11.23)

        self.assertEqual(obs.data.wind_dir, 296.0)
        self.assertEqual(obs.data["wind_dir"], 296.0)

        data['temperature'] = 94.4
        obs.data = data
        self.assertEqual(obs.data.temperature, 94.4)

        obs.data.temperature = 54.9
        self.assertEqual(obs.data.temperature, 54.9)

    def test_reject_invalid_data(self):
        """Test adding invalid measurements to observation."""
        ts = datetime.datetime.utcnow()
        data = {
            "temperature": 262.0,
            "humidity": 45.0,
            "dewpoint": 50.0,
            "pressure": 29.123,
            "rain_rate": 0.12,
            "daily_rain": 0.46,
            "wind_speed": 943.00,
            "wind_dir": 296.0,
        }
        obs = Observation(ts, data)

        self.assertRaises(KeyError, self.__get_item, obs.data, 'temperature')
        self.assertRaises(KeyError, self.__get_item, obs.data, 'wind_speed')

        obs.data['pressure'] = 94.56
        self.assertEqual(obs.data.pressure, 29.123)

        obs.data.pressure = 94.56
        self.assertEqual(obs.data.pressure, 29.123)


    def test_update(self):
        """Test update observation."""

        ts = datetime.datetime.utcnow()
        data = {
            "temperature": 60.0,
            "humidity": 45.0,
        }
        obs = Observation(ts, data)
        data = {
            "temperature": 70.0,
            "humidity": 55.0,
        }
        obs.update(data)
        self.assertEqual(obs.data.temperature, 65.0)
        self.assertEqual(obs.data.humidity, 50.0)

        data = {
            "temperature": 80.0,
        }
        obs.update(data)
        self.assertEqual(obs.data.temperature, 70.0)
        self.assertRaises(KeyError, self.__get_item, obs.data, 'humidity')

    def test_serialize(self):
        """Test serializing observation"""
        ts = datetime.datetime.utcnow()
        data = {
            "temperature": 62.0,
            "humidity": 45.0,
            "dewpoint": 50.0,
            "pressure": 29.123,
            "rain_rate": 0.12,
            "daily_rain": 0.46,
            "wind_speed": 11.23,
            "wind_dir": 296.0
        }
        obs = Observation(ts, data)
        serialized = obs.as_dict()

        self.assertEqual(serialized['time_stamp'], ts)
        self.assertEqual(serialized['temperature'], 62.0)
        self.assertEqual(serialized['humidity'], 45.0)
        self.assertEqual(serialized['dewpoint'], 50.0)
        self.assertEqual(serialized['pressure'], 29.123)
        self.assertEqual(serialized['rain_rate'], 0.12)
        self.assertEqual(serialized['daily_rain'], 0.46)
        self.assertEqual(serialized['wind_speed'], 11.23)
        self.assertEqual(serialized['wind_dir'], 296.0)

    def test_add_maxes(self):
        """Test calculation of maxes"""
        ts = datetime.datetime.utcnow()
        data = {
            'temperature': 45,
            'humidity': 32,
            'wind_speed': 10,
        }
        obs = Observation(ts, data, maxes=['wind_speed'])
        self.assertEqual(obs.maxes['wind_speed'], data['wind_speed'])

        data = {
            'temperature': 45,
            'humidity': 32,
            'wind_speed': 17,
        }
        obs.update(data)
        self.assertEqual(obs.maxes['wind_speed'], 17)

        data = {
            'temperature': 45,
            'humidity': 32,
            'wind_speed': 9,
        }
        obs.update(data)
        self.assertEqual(obs.maxes['wind_speed'], 17)

        data = {
            'temperature': 67,
            'humidity': 32,
            'wind_speed': 22,
        }
        obs.update(data)
        self.assertEqual(obs.maxes['wind_speed'], 22)

        obj = obs.as_dict()
        self.assertEqual(obj['max_wind_speed'], 22)

        data = {
            'temperature': 67,
            'humidity': 32,
        }
        obs.update(data)
        self.assertRaises(KeyError, self.__get_item, obs.maxes, 'wind_speed')

        obs = Observation(ts, data, maxes=['wind_speed'])
        self.assertRaises(KeyError, self.__get_item, obs.maxes, 'wind_speed')

        obs = Observation(ts, data, maxes=['temperature'])
        self.assertEqual(obs.data['temperature'],  obs.maxes['temperature'])
        obs.data = {'humidity': 40}
        self.assertRaises(KeyError, self.__get_item, obs.maxes, 'temperature')

