import pika 
import config as cfg
import json
import pickle
from sklearn.ensemble import RandomForestClassifier

credentials = pika.PlainCredentials(cfg.RABBIT_USER, cfg.RABBIT_PASSWORD)
connection_parameters = pika.ConnectionParameters(host='127.0.0.1', port=cfg.RABBIT_PORT, credentials=credentials)
connection = pika.BlockingConnection(connection_parameters)
channel = connection.channel()

channel.queue_declare(queue=cfg.MAIN_TOPIC)

def on_message_received(ch, method, properties, body):
  try:
    req = json.loads(body)
    req['model'] = []
    print(str(req)[:500])
  except Exception as e:
    print(e)

def serialize_model(model):
  return list(pickle.dumps(model))

message = {
  "modelLabel": cfg.STATUS_CREATE,
  "modelId": "123", 
  "classifier": "RandomForestClassifier", 
  "options": [{"descriptionFlag": "n_estimators", "description": "100"}]
}

channel.basic_publish(exchange='', routing_key=cfg.TOPIC_NAME, body=json.dumps(message))
print('Create model')

message = {
  "modelLabel": cfg.STATUS_TRAIN,
  "modelId": "123", 
  "model": serialize_model(RandomForestClassifier()), 
  "features": [[1, 0, 1], [1, 1, 0], [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 0, 0], [1, 0, 1], [1, 1, 0]],
  "labels": [1, 1, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1]
}
channel.basic_publish(exchange='', routing_key=cfg.TOPIC_NAME, body=json.dumps(message))
print('Train model')

clf = RandomForestClassifier()
clf = clf.fit([[1, 0, 1], [1, 1, 0], [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 0, 0], [1, 0, 1], [1, 1, 0]], [1, 1, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1])

message = {
  "modelLabel": cfg.STATUS_PREDICT,
  "modelId": "123", 
  "model": serialize_model(clf), 
  "features": [[1, 0, 1], [1, 0, 0]]
}

channel.basic_publish(exchange='', routing_key=cfg.TOPIC_NAME, body=json.dumps(message))
print('Model predict')

channel.basic_consume(queue=cfg.MAIN_TOPIC, auto_ack=True, on_message_callback=on_message_received)

print("Starting Consuming")

channel.start_consuming()

connection.close()