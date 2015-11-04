from yapsy.IPlugin import IPlugin

class MockEmitter1(IPlugin):
    @classmethod
    def connect(cls):
        return cls()

    def send(self):
        return True
