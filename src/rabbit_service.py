import pika
import json


class RabbitService:
    def __init__(self, host, port, user, password):
        credentials = pika.PlainCredentials(user, password)
        connection_parameters = pika.ConnectionParameters(
            host=host, port=port, credentials=credentials)
        self.connection = pika.BlockingConnection(connection_parameters)
        self.channel = self.connection.channel()

    def __del__(self):
        self.connection.close()

    def add_topic(self, topic_name):
        self.channel.queue_declare(queue=topic_name)

    def send_message(self, topic_name, message):
        self.channel.basic_publish(
            exchange='',
            routing_key=topic_name,
            body=json.dumps(message)
        )

    def start_consuming(self, topic_name, callback_func, auto_ack=False):
        self.channel.basic_consume(
                queue=topic_name, auto_ack=auto_ack, on_message_callback=callback_func)
        self.channel.start_consuming()