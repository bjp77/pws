import pluginbase
import inspect
import importlib #not sure if this is really needed. 
import logging
import json
import time
from mongo import Database

DEFAULT_POLLING_INTERVAL = 60

class Observer(object):
    def __init__(self):
        """Iterate over available PWS console plugins.  Once a plugin
        is found that returns a connection object from its discover method,
        create an instance of the discovered console.
        """
        #TODO Load config file
        self.polling_interval = DEFAULT_POLLING_INTERVAL
        self.db = Database()   
        self.console = self._find_console()
        self.emitters = self._find_emitters()

    def _find_console(self):
        """Look for available console."""
        console = None

        plugin_base = pluginbase.PluginBase('console_models')
        plugin_source = plugin_base.make_plugin_source(
           searchpath=['./consoles'])

        for plugin in plugin_source.list_plugins():
            #console_plugin = plugin_source.load_plugin(plugin)
            console_plugin = importlib.import_module('consoles.'+plugin)
            for cnsl_name, cnsl_class in inspect.getmembers(console_plugin,
                                                            inspect.isclass):
                if  not hasattr(cnsl_class, 'discover'):
                    continue

                console = cnsl_class.discover()
                if console is not  None:
                    return console

        # No console found
        return console

    def _find_emitters(self):
        """Look for available emitter plugins"""
        emitters = []

        plugin_base = pluginbase.PluginBase('emitters')
        plugin_source = plugin_base.make_plugin_source(
           searchpath=['./emitters'])

        for plugin in plugin_source.list_plugins():
            #emitter_plugin = plugin_source.load_plugin(plugin)
            emitter_plugin = importlib.import_module('emitters.'+plugin)
            for emit_name, emit_class in inspect.getmembers(emitter_plugin,
                                                            inspect.isclass):
                    if not hasattr(emit_class, 'connect'):
                        continue

                    emitter = emit_class.connect()
                    if emitter != None:
                        emitters.append(emitter)

        return emitters

    def run(self):
        """Start PWS monitor service"""
        while True:
            #TODO Apply filters to obersvation data
            #TODO Backfill and resume after connection failure
            obs = self.console.measure()
            self.db.save(obs)
            for emitter in self.emitters:
                emitter.send(obs)
            time.sleep(self.polling_interval)

if __name__ == '__main__':
    Observer().run()
