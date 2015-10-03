from yapsy.IPlugin import IPlugin

class MockConsole(IPlugin):
    @classmethod
    def discover(cls):
        return cls()

    def measure(self):
        return {'temperature': 0}
