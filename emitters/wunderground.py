import configparser
import requests
import urllib

class Wunderground(object):

    _mapper = {
        'Temperature': '&tempf={0}',
        'Humidity': '&humidity={0}',
    }

    _base_url_spec = ('http://weatherstation.wunderground.com/weatherstation/'
                      'updateweatherstation.php?ID={0}&PASSWORD={1}&dateutc={2}'
                      ',action=updateraw')

    def __init__(self, station, password):
        self._station = station
        self._password = password
    
    def _build_url(self, data):
        dateutc = urllib.quote(str(data['Time']).split('.')[0])
        url = self._base_url_spec.format(self._station, self._password, dateutc)

        for key in self._mapper:
            try:
                url += self._mapper[key].format(data[key])
            except KeyError:
                pass

        return url

    @classmethod
    def connect(cls):
        f = '/etc/opt/pws/emitters/wunderground.conf'
        conf = configparser.ConfigParser()
        conf.read(f)
        station = conf.get('WUConfig', 'station')
        password = conf.get('WUConfig', 'password')
        r = requests.get(cls._base_url_spec.format(station, password, 'now'))
        if r.status_code == requests.codes.ok:
            return cls(station, password)
        else:
            return None

    def send(self, data):
        r = requests.get(self._build_url(data))
        print r.text
        return r.status_code == requests.codes.ok
