import pluginbase
import inspect
import importlib #not sure if this is really needed. 
import logging
import json
import time
from mongo import Database
import logging

logging.basicConfig(filename='/var/log/pwsobs.log',
                    format='%(levelname)s:%(asctime)s %(message)s')
log = logging.getLogger()
log.setLevel(logging.DEBUG)

class Observer(object):
    CNSL_PLUGIN_PATH = './consoles'
    EMIT_PLUGIN_PATH = './emitters'
    CNSL_PLUGIN_BASE = 'console_models'
    EMIT_PLUGIN_BASE = 'emitter_types'
    CNSL_PKG_SPEC = 'consoles.{0}'
    EMIT_PKG_SPEC = 'emitters.{0}'
    DISCOVER_METHOD = 'discover'
    CONNECT_METHOD = 'connect'

    class _valid_range():
        def __init__(self, min, max):
            self.min = min
            self.max = max

        def __call__(self, val):
            return val >= self.min and val <= self.max

    _valid = {
        'Temperature': _valid_range(-100, 150),
        'Humidity': _valid_range(0, 100),
        'Pressure': _valid_range(20, 32.5),
        'RainRate': _valid_range(0, 10.0),
        'DailyRain': _valid_range(0, 10.0),
        'WindSpeed': _valid_range(0, 200),
        'WindDir': _valid_range(0, 360),
        'WindGustSpeed': _valid_range(0, 200),
        'WindGustDir': _valid_range(0, 360),
        'Dewpoint': _valid_range(-100, 150),
    }

    def __init__(self, find_cnsl=True, find_emitters=True, polling_interval=240):
        """Iterate over available PWS console plugins.  Once a plugin
        is found that returns a connection object from its discover method,
        create an instance of the discovered console.
        """
        #TODO Load config file
        self.polling_interval = polling_interval
        self.db = Database()   
        if find_cnsl:
            self.console = self.find_console()
        if find_emitters:
            self.emitters = self.find_emitters()

    def find_console(self):
        """Look for available console."""
        console = None

        plugin_base = pluginbase.PluginBase(self.CNSL_PLUGIN_BASE)
        plugin_source = plugin_base.make_plugin_source(
           searchpath=[self.CNSL_PLUGIN_PATH])

        for plugin in plugin_source.list_plugins():
            logging.debug('Found potential console plugin: {0}'.format(plugin))
            #console_plugin = plugin_source.load_plugin(plugin)
            console_plugin = importlib.import_module(
                self.CNSL_PKG_SPEC.format(plugin))
            for cnsl_name, cnsl_class in inspect.getmembers(console_plugin,
                                                            inspect.isclass):
                if not hasattr(cnsl_class, self.DISCOVER_METHOD):
                    continue

                logging.debug('Class {0} has discover method'.format(cnsl_name))
                console = cnsl_class.discover()
                if console is not  None:
                    logging.info('Discovered {0} console.'.format(cnsl_name))
                    return console
                else:
                    logging.warning('No {0} console found.'.format(cnsl_name))

        logging.error('No consoles found.')
        # No console found
        return console

    def find_emitters(self):
        """Look for available emitter plugins"""
        emitters = []

        plugin_base = pluginbase.PluginBase(self.EMIT_PLUGIN_BASE)
        plugin_source = plugin_base.make_plugin_source(
           searchpath=[self.EMIT_PLUGIN_PATH])

        for plugin in plugin_source.list_plugins():
            #emitter_plugin = plugin_source.load_plugin(plugin)
            logging.debug('Found potential emit plugin {0}'.format(plugin))
            emitter_plugin = importlib.import_module(
                self.EMIT_PKG_SPEC.format(plugin))
            for emit_name, emit_class in inspect.getmembers(emitter_plugin,
                                                            inspect.isclass):
                if not hasattr(emit_class, self.CONNECT_METHOD):
                    continue

                logging.debug('Class {0} has connect method'.format(emit_name))
                emitter = emit_class.connect()
                if emitter != None:
                    logging.info('Connected to {0} emitter'.format(emit_name))
                    emitters.append(emitter)
                else:
                    logging.warning('No {0} emitter found'.format(emit_name))

        if len(emitters) == 0:
            logging.warning('No emitters found')

        return emitters

    def _validate_obs(self, obs):
        del_key_list = []
        for key in obs:
            if key == 'Time':
                continue

            try:
                if not self._valid[key](obs[key]):
                    logging.error('{0} value {1} is out of range'. \
                        format(key, obs[key]))
                    del_key_list.append(key)
            except KeyError:
                logging.debug('{0} raises KeyError.'.format(key))

        for key in del_key_list:
            obs.pop(key, None)

    def run(self):
        """Start PWS monitor service"""
        while True:
            #TODO Apply filters to obersvation data
            #TODO Backfill and resume after connection failure
            obs = self.console.measure()
            logging.debug(obs)
            self._validate_obs(obs)
            self.db.save(obs)
            for emitter in self.emitters:
                emitter.send(obs)
            time.sleep(self.polling_interval)

if __name__ == '__main__':
    Observer().run()
