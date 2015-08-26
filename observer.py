import inspect
import importlib #not sure if this is really needed. 
import logging
import json
import time
from mongo import Database
import logging
import gevent
import pluginbase
import datetime
from observation import Observation

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

    def __init__(self, find_cnsl=True, find_emitters=True, poll_interval=5, emit_interval=60):
        """Iterate over available PWS console plugins.  Once a plugin
        is found that returns a connection object from its discover method,
        create an instance of the discovered console.
        """
        #TODO Load config file
        self.poll_interval = poll_interval
        self.emit_interval = emit_interval
        self._obs = None
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

    def _emit(self):
        while True:
            if self._obs is not None:
                obs = self._obs.as_dict()
                self.db.save(obs)
                for emitter in self.emitters:
                    emitter.send(obs)
                self._obs = None
                gevent.sleep(self.emit_interval)

    def _poll(self):
        """Start PWS monitor service"""
        while True:
            #TODO Apply filters to obersvation data
            #TODO Backfill and resume after connection failure
            if self._obs is None:
                ts = datetime.datetime.utcnow()
                obs = self.console.measure()
                self._obs = Observation(ts, obs, maxes=['wind_speed'])
            else:
                self._obs.update(self.console.measure())
            gevent.sleep(self.poll_interval)

    def start(self):
        threads = [gevent.spawn(self._poll),
                   gevent.spawn(self._emit)]
        print threads
        gevent.joinall(threads)

if __name__ == '__main__':
    Observer().start()

