from yapsy.IPlugin import IPlugin

class MockEmitter2(IPlugin):
    @classmethod
    def connect(cls):
        return cls()

    def send(self):
        return True
