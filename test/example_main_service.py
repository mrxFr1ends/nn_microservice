import os, sys
sys.path.insert(1, os.path.join(sys.path[0], '..'))

import pika
from config import Rabbit, MainTopic, Provider, RequestStatus
import json
import pickle
from sklearn.ensemble import RandomForestClassifier

from rabbit_service import RabbitService

def on_message_received(ch, method, properties, body):
    print(f"Received {len(body)} bytes")
    try:
        req = json.loads(body)
        if 'model' in req: req['model'] = []
        print(str(req)[:500])
    except Exception as e:
        print(e)

service = RabbitService()
print("[*] Starting Consuming")
service.start_consuming(callback_func=on_message_received)

credentials = pika.PlainCredentials(Rabbit.USER, Rabbit.PASSWORD)
connection_parameters = pika.ConnectionParameters(
    host=Rabbit.HOST, port=Rabbit.PORT, credentials=credentials)
connection = pika.BlockingConnection(connection_parameters)
channel = connection.channel()

channel.queue_declare(queue=MainTopic.MAIN)


def serialize_model(model):
    return list(pickle.dumps(model))


message = {
    "modelLabel": RequestStatus.CREATE,
    "modelId": "123",
    "classifier": "RandomForestClassifier",
    "options": [{"descriptionFlag": "n_estimators", "description": "100"}]
}

channel.basic_publish(
    exchange='', routing_key=Provider.TOPIC_NAME, body=json.dumps(message))
print('Create model')

message = {
    "modelLabel": RequestStatus.TRAIN,
    "modelId": "123",
    "model": serialize_model(RandomForestClassifier()),
    "features": [[1, 0, 1], [1, 1, 0], [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 0, 0], [1, 0, 1], [1, 1, 0]],
    "labels": [1, 1, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1]
}
channel.basic_publish(
    exchange='', routing_key=Provider.TOPIC_NAME, body=json.dumps(message))
print('Train model')

clf = RandomForestClassifier()
clf = clf.fit([[1, 0, 1], [1, 1, 0], [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 0, 0], [
              1, 0, 1], [1, 1, 0], [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 0, 0], [1, 0, 1], [1, 1, 0]], [1, 1, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1])

message = {
    "modelLabel": RequestStatus.PREDICT,
    "modelId": "123",
    "model": serialize_model(clf),
    "features": [[1, 0, 1], [1, 0, 0]]
}

channel.basic_publish(
    exchange='', routing_key=Provider.TOPIC_NAME, body=json.dumps(message))
print('Model predict')

channel.basic_consume(queue=MainTopic.MAIN, auto_ack=True,
                      on_message_callback=on_message_received)

print("Starting Consuming")

channel.start_consuming()

connection.close()
