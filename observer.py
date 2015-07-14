import pluginbase
import inspect
import importlib #not sure if this is really needed. 
import logging
import json
import time
from mongo import Database

class Observer(object):
    def __init__(self):
        """Iterate over available PWS console plugins.  Once a plugin
        is found that returns a connection object from its discover method,
        create an instance of the discovered console.
        """
        self.db = Database()   

        plugin_base = pluginbase.PluginBase('console_models')
        plugin_source = plugin_base.make_plugin_source(
           searchpath=['./consoles'])

        for plugin in plugin_source.list_plugins():
            #console_plugin = plugin_source.load_plugin(plugin)
            console_plugin = importlib.import_module('consoles.'+plugin)
            for cnsl_name, cnsl_class in inspect.getmembers(console_plugin,
                                                            inspect.isclass):
                conn = cnsl_class.discover()
                if conn != None:
                    self.console = cnsl_class(conn) 
                    return

    def run(self):
        """Start PWS monitor service"""
        while True:
            obs = self.console.measure()
            self.db.save(obs)
            time.sleep(60)

if __name__ == '__main__':
    Observer().run()
