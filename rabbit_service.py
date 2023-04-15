import pika
import config as cfg
import json

class RabbitService:
  def __init__(self):
    connection_parameters = pika.ConnectionParameters(cfg.RABBIT_HOST)
    self.connection = pika.BlockingConnection(connection_parameters)
    self.channel = self.connection.channel()
    self.channel.queue_declare(queue=cfg.MAIN_TOPIC)
    self.channel.queue_declare(queue=cfg.ERROR_TOPIC)
    self.channel.queue_declare(queue=cfg.TOPIC_NAME)
    
  def __del__(self):
    self.connection.close()

  def send_message(self, topic_name, message):
    self.channel.basic_publish(
      exchange='', 
      routing_key=topic_name, 
      body=json.dumps(message)
    )

  def start_consuming(self, callback_func):
    self.channel.basic_consume(queue=cfg.TOPIC_NAME, auto_ack=True, on_message_callback=callback_func)
    self.channel.start_consuming()