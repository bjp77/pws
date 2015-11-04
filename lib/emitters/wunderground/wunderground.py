import configparser
import requests
import urllib
import logging
from yapsy.IPlugin import IPlugin

class Wunderground(IPlugin):

    _mapper = {
        'temperature': '&tempf={0:.2f}',
        'humidity': '&humidity={0:.2f}',
        'dewpoint': '&dewptf={0:.2f}',
        'pressure': '&baromin={0:.3f}',
        'rain_rate': '&rainin={0:.2f}',
        'daily_rain': '&dailyrainin={0:.2f}',
        'wind_speed': '&windspeedmph={0:.2f}',
        'wind_dir': '&winddir={0:.0f}',
        'max_wind_speed': '&windgustmph={0:.2f}',
    }

    _base_url_spec = ('http://weatherstation.wunderground.com/weatherstation/'
                      'updateweatherstation.php?ID={0}&PASSWORD={1}&dateutc={2}'
                      ',action=updateraw')

    def __init__(self, station, password):
        self._station = station
        self._password = password
    
    def _build_url(self, data):
        dateutc = urllib.quote(str(data['time_stamp']).split('.')[0])
        url = self._base_url_spec.format(self._station, self._password, dateutc)

        for key in self._mapper:
            try:
                url += self._mapper[key].format(data[key])
            except KeyError:
                logging.error('{0} not found'.format(key))

        return url

    @classmethod
    def connect(cls, config=None):
        if not config:
            return None
        
        conf = configparser.ConfigParser()
        conf.read(config)
        station = conf.get('WUConfig', 'station')
        password = conf.get('WUConfig', 'password')
        for i in xrange(0, 5):
            try:
                r = requests.get(cls._base_url_spec.format(station,
                                                           password, 'now'))
                if r.status_code == requests.codes.ok:
                    return cls(station, password)
            except Exception as e:
                logging.error(e)
        else:
            return None

    def send(self, data):
        try:
            r = requests.get(self._build_url(data))
            return r.status_code == requests.codes.ok
        except Exception as e:
            logging.error(e)
            return False
