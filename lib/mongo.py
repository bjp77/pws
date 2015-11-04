import pymongo

class Database(object):
    def __init__(self, address='localhost', port=27017):
        client = pymongo.MongoClient(address, port)
        self.db = client.weather

    def save(self, data):
        self.db.observations.insert_one(data)
