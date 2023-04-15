import pika 
import config as cfg

def on_message_received(ch, method, properties, body):
  print(f"[!] Received message: {body}")

connection_parameters = pika.ConnectionParameters(cfg.RABBIT_HOST)
connection = pika.BlockingConnection(connection_parameters)
channel = connection.channel()

channel.queue_declare(queue=cfg.REGISTER_TOPIC)
channel.basic_consume(queue=cfg.REGISTER_TOPIC, auto_ack=True, on_message_callback=on_message_received)

print("Starting Consiming")

channel.start_consuming()