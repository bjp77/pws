import inspect
import logging
import json
import time
from mongo import Database
import logging
import gevent
import datetime
from yapsy.PluginManager import PluginManager
from observation import Observation

logging.basicConfig(filename='/var/log/pwsobs.log',
                    format='%(levelname)s:%(asctime)s %(message)s')
log = logging.getLogger()
log.setLevel(logging.DEBUG)

CNSL_PLUGIN_PATH = 'consoles'
EMIT_PLUGIN_PATH = 'emitters'

class ObsPluginManager(PluginManager):
    def instanciateElement(self, element):
        if hasattr(element, 'discover'):
            return element.discover()
        elif hasattr(element, 'connect'):
            return element.connect()
        return None

class Observer(object):
    def __init__(self, console_path=CNSL_PLUGIN_PATH, find_cnsl=True, 
                 emitter_path=EMIT_PLUGIN_PATH, find_emitters=True, 
                 poll_interval=5, emit_interval=60):
        """Iterate over available PWS console plugins.  Once a plugin
        is found that returns a connection object from its discover method,
        create an instance of the discovered console.
        """
        #TODO Load config file
        self.poll_interval = poll_interval
        self.emit_interval = emit_interval
        self._obs = None
        self.db = Database()
        self.console = None
        self._console_path = console_path
        self.emitters = []
        self._emitter_path = emitter_path
        if find_cnsl:
            self.find_console()
        if find_emitters:
            self.find_emitters()

    def find_console(self):
        """Look for available console."""
        plugin_manager = ObsPluginManager()
        plugin_manager.setPluginPlaces([self._console_path])
        plugin_manager.collectPlugins()

        for plugin in plugin_manager.getAllPlugins():
            logging.debug('Found potential console plugin: {0}'.format(plugin.plugin_object))
            if hasattr(plugin.plugin_object, 'discover'):
                logging.debug('Class {0} has discover method'.format(plugin.plugin_object))
                self.console = plugin.plugin_object.discover()
                if self.console is not None:
                    break

        if not self.console:
            logging.warning('No consoles found.')

    def find_emitters(self):
        """Look for available emitter plugins"""
        plugin_manager = ObsPluginManager()
        plugin_manager.setPluginPlaces([self._emitter_path])
        plugin_manager.collectPlugins()

        for plugin in plugin_manager.getAllPlugins():
            logging.debug('Found potential console plugin: {0}'.format(plugin.plugin_object))
            if hasattr(plugin.plugin_object, 'connect'):
                logging.debug('Class {0} has connect method'.format(plugin.plugin_object))
                emitter = plugin.plugin_object.connect()
                if emitter is not None:
                    self.emitters.append(emitter)

        if not self.emitters:
            logging.warning('No emitters found.')

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

