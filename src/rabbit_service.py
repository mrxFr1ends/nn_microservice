import pika
from config import Rabbit, Provider, MainTopic
import json


class RabbitService:
    def __init__(self):
        credentials = pika.PlainCredentials(Rabbit.USER, Rabbit.PASSWORD)
        connection_parameters = pika.ConnectionParameters(
            host=Rabbit.HOST, port=Rabbit.PORT, credentials=credentials)
        self.connection = pika.BlockingConnection(connection_parameters)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=MainTopic.MAIN)
        self.channel.queue_declare(queue=MainTopic.ERROR)
        self.channel.queue_declare(queue=Provider.TOPIC_NAME)

    def __del__(self):
        self.connection.close()

    def send_message(self, topic_name, message):
        self.channel.basic_publish(
            exchange='',
            routing_key=topic_name,
            body=json.dumps(message)
        )

    def start_consuming(self, callback_func):
        self.channel.basic_consume(
            queue=Provider.TOPIC_NAME, auto_ack=True, on_message_callback=callback_func)
        self.channel.start_consuming()
