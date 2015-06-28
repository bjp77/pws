import pluginbase
import inspect
import threading
import logging

logging.basicConfig(level=logging.DEBUG)

class Observer(threading.Thread):
    def __init__(self):
        """Iterate over available PWS console plugins.  Once a plugin
        is found that returns a connection object from its discover method,
        create an instance of the discovered console.
        """
        super(Observer, self).__init__(name='PWS Observer Daemon')
	#self.daemon = True
	
        plugin_base = pluginbase.PluginBase('console_models')
        plugin_source = plugin_base.make_plugin_source(
           searchpath=['./consoles'])

        for plugin in plugin_source.list_plugins():
            console_plugin = plugin_source.load_plugin(plugin)
            for cnsl_name, cnsl_class in inspect.getmembers(console_plugin,
                                                            inspect.isclass):
                conn = cnsl_class.discover()
                if conn != None:
                    self.console = cnsl_class(conn) 
                    return

    def run(self):
        """Start PWS monitor service"""
        print "I'm a daemon!"
	open('test_file.txt', 'w').write('ha!')

if __name__ == '__main__':
    Observer().start()
