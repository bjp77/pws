import logging
import json
import time
import logging
import datetime
from pws.lib import Observation
import sys
import pika

logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s')
log = logging.getLogger()
log.setLevel(logging.DEBUG)

class Observer(object):
    def __init__(self, poll_interval=5, pub_interval=60, amqp=None, **kwargs):
        """Iterate over available PWS console plugins.  Once a plugin
        is found that returns a connection object from its discover method,
        create an instance of the discovered console.
        """
        self.poll_interval = poll_interval
        self.pub_interval = pub_interval
        self._obs = None
        self._init_messenger(amqp)
    
    def _init_messenger(self, config):
        #todo error handling
        credentials = pika.PlainCredentials(config['user'], config['password'])
        parameters = pika.ConnectionParameters(config['host'], config['port'], '/', credentials)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.exchange_declare(exchange='obs', type='topic')

        def publish(message):
            message_str = json.dumps(message)
            #if not channel.is_open:
            #    channel.open()
            channel.basic_publish(exchange=config['exchange'], routing_key=config['routing_key'], body=message_str)
            #channel.close()
        
        self.publish = publish

    @classmethod
    def discover(cls, config=None):
        raise NotImplementedError()

    def measure(self):
        raise NotImplementedError();

    def poll(self):
        """Start PWS monitor service"""
        pub_time = time.time()
        while True:
            #TODO Apply filters to obersvation data
            #TODO Backfill and resume after connection failure
            if self._obs is None:
                ts = datetime.datetime.utcnow()
                obs = self.measure()
                self._obs = Observation(ts, obs, maxes=['wind_speed'])
            else:
                self._obs.update(self.measure())
            
            if time.time() - pub_time >= self.pub_interval:
                self.publish(self._obs.as_dict())
                self._obs = None
                pub_time = time.time()
            
            time.sleep(self.poll_interval)
