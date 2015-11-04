from datetime import datetime
import pika
import yaml
import json

class Reporter(object):
    def __init__(self, amqp=None, **kwargs):
        self._init_messenger(amqp)

    @classmethod
    def connect(cls, config=None):
        raise NotImplementedError()

    def send(self, data):
        raise NotImplementedError()

    def _init_messenger(self, config):
        #todo error handling
        credentials = pika.PlainCredentials(config['user'], config['password'])
        parameters = pika.ConnectionParameters(config['host'], config['port'], '/', credentials)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.exchange_declare(exchange=config['exchange'], type='topic')
        result = channel.queue_declare(exclusive=True)
        self._queue_name = result.method.queue
        channel.queue_bind(exchange='obs',
                           queue=self._queue_name,
                           routing_key=config['routing_key'])
        self._channel = channel

    def listen(self):
        #if not self.__channel.is_open:
        #    self.__channel.open()
        def callback(ch, method, properties, body):
            message = json.loads(body)
           
            message['time_stamp'] = datetime.strptime(message['time_stamp'],
                                                      '%Y-%m-%d %H:%M:%S.%f')
            success = self.send(message)
            if success:
                self._channel.basic_ack(delivery_tag=method.delivery_tag)
            else:
                self._channel.basic_nack(delivery_tag=method.delivery_tag)
        self._channel.basic_consume(callback, self._queue_name)
        self._channel.start_consuming()
