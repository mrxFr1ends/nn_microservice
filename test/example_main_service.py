import os, sys
sys.path.insert(1, os.path.join(sys.path[0], '..'))

import pika
from config import *
import json
from sklearn.ensemble import RandomForestClassifier
from src.utils import serialize_model
from sklearn.datasets import make_classification
from src.rabbit_service import RabbitService

algorithms_taken = False

def on_message_received(channel, method, properties, body):
    print(f"Received {len(body)} bytes")

    try:
        req = json.loads(body)
    except Exception as e:
        print(e)
        return 

    global algorithms_taken
    if algorithms_taken == False:
        algorithms = req['algorithms']
        print(algorithms)
        algorithms_taken = True
        channel.stop_consuming()
    else:
        try:
            # Just for less trash
            req['model_size'] = len(req['model'])
            req['model'] = len(req['model'])
            print(str(req)[:500])
        except Exception as e:
            print(e)
            return

    channel.basic_ack(method.delivery_tag)

service = RabbitService('127.0.0.1', Rabbit.PORT, Rabbit.USER, Rabbit.PASSWORD)
service.add_topic(MainTopic.MAIN)
service.add_topic(MainTopic.ERROR)
service.add_topic(Provider.TOPIC_NAME)

print(f"[*] Starting Consuming {MainTopic.MAIN}")
service.start_consuming(MainTopic.MAIN, callback_func=on_message_received)

MESSAGE_CREATE = {
    "modelLabel": RequestStatus.CREATE,
    "modelId": "123",
    "classifier": "RandomForestClassifier",
    "options": [
        {"descriptionFlag": "n_estimators", "description": "100"},
        {"descriptionFlag": "criterion", "description": "gini"},
        {"descriptionFlag": "class_weight", "description": "[1, 2]"}
    ]
}

MESSAGE_TRAIN = {
    "modelLabel": RequestStatus.TRAIN,
    "modelId": "123",
    "model": serialize_model(RandomForestClassifier()),
}
x, y = make_classification(n_samples=20, n_features=5)
MESSAGE_TRAIN["features"], MESSAGE_TRAIN["labels"] = x.tolist(), y.tolist()

clf = RandomForestClassifier()
x, y = make_classification(n_samples=20, n_features=5)
clf = clf.fit(x, y)
MESSAGE_PREDICT = {
    "modelLabel": RequestStatus.PREDICT,
    "modelId": "123",
    "model": serialize_model(clf),
    "features": x[:4].tolist()
}


service.send_message(Provider.TOPIC_NAME, MESSAGE_CREATE)
print('Create model')

service.send_message(Provider.TOPIC_NAME, MESSAGE_TRAIN)
print('Train model')

service.send_message(Provider.TOPIC_NAME, MESSAGE_PREDICT)
print('Model predict')

print(f"[*] Starting Consuming {MainTopic.MAIN}")
service.start_consuming(MainTopic.MAIN, callback_func=on_message_received)