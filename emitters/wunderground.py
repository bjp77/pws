class Wunderground(object):
    def __init__(self):
        print "I'm a Wunderground Emitter!"
    
    @classmethod
    def connect(cls):
        return cls()

    def send(self, data):
        print data
