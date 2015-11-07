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
import sys
import os

logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s')
log = logging.getLogger()
log.setLevel(logging.DEBUG)

CNSL_PLUGIN_PATH = 'pws/lib/consoles'
EMIT_PLUGIN_PATH = 'pws/lib/emitters'

class ObsPluginManager(PluginManager):
    def instanciateElement(self, element):
        """
        Just return the class object and use factory method
        to instanciate element later.
        """
        return element

class Observer(object):
    def __init__(self, console_path=CNSL_PLUGIN_PATH, find_cnsl=True, 
                 emitter_path=EMIT_PLUGIN_PATH, find_emitters=True, 
                 poll_interval=5, emit_interval=60, plugin_conf=None):
        """Iterate over available PWS console plugins.  Once a plugin
        is found that returns a connection object from its discover method,
        create an instance of the discovered console.
        """
        self.poll_interval = poll_interval
        self.emit_interval = emit_interval
        self._obs = None
        self.db = Database()
        self.console = None
        self._console_path = console_path
        self.emitters = []
        self._emitter_path = emitter_path
        if not plugin_conf:
            self.plugin_conf={}
        else:
            self.plugin_conf = plugin_conf

        if find_cnsl:
            self.find_console()
        if find_emitters:
            self.find_emitters()

    @staticmethod
    def _find_directory(relpath):
        """
        This ugliness is needed to figure out the full path of
        console and emitter plugins.  This assmes that they have been
        installed in site-packages or dist-packages.

        I can't help but think there is a better way to do this, but
        this will work for now.
        """
        for path in sys.path:
            if path.endswith('-packages'):
                contents = os.listdir(path)
                for item in contents:
                    full_item_path = os.path.join(path, item)
                    if os.isdir(full_item_path) and \
                       item.startswith('pws') and \
                       os.isdir(os.path.join(full_item_path, relpath)):
                        return os.path.join(full_item_path, relpath)
        return None

    def find_console(self):
        """Look for available console."""
        abs_console_path = self._find_directory(self._console_path)
        plugin_manager = ObsPluginManager()
        plugin_manager.setPluginPlaces([abs_console_path])
        plugin_manager.collectPlugins()

        for plugin in plugin_manager.getAllPlugins():
            logging.debug('Found potential console plugin: {0}'.format(plugin.plugin_object))
            if hasattr(plugin.plugin_object, 'discover'):
                logging.debug('Class {0} has discover method'.format(plugin.plugin_object))
                self.console = \
                    plugin.plugin_object.discover(config=self.plugin_conf.get(plugin.name, None))
                if self.console is not None:
                    break

        if not self.console:
            logging.warning('No consoles found.')

    def find_emitters(self):
        """Look for available emitter plugins"""
        abs_emitter_path = self._find_directory(self._emitter_path)
        plugin_manager = ObsPluginManager()
        plugin_manager.setPluginPlaces([abs_emitter_path])
        plugin_manager.collectPlugins()

        for plugin in plugin_manager.getAllPlugins():
            logging.debug('Found potential console plugin: {0}'.format(plugin.plugin_object))
            if hasattr(plugin.plugin_object, 'connect'):
                logging.debug('Class {0} has connect method'.format(plugin.plugin_object))
                emitter = \
                    plugin.plugin_object.connect(config=self.plugin_conf.get(plugin.name, None))
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

