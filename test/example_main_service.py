import traceback
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier
import json
from utils import *
from rabbit_service import *
from config import *
from request_handlers import *
from classificator import *
import os
import sys
sys.path.insert(1, os.path.join(sys.path[0], '../src'))


algorithms_taken = False


def on_message_received(channel, method, properties, body):
    print(f"Received {len(body)} bytes")

    try:
        req = json.loads(body)
    except Exception as e:
        print(e)
        return

    try:
        global algorithms_taken
        if algorithms_taken == False:
            algorithms = req['algorithms']
            print(len(algorithms))
            algorithms_taken = True
            channel.stop_consuming()
        else:
            # Just for less trash
            req['serializedModelData']['model'] = len(
                req['serializedModelData']['model'])
            print(str(req)[:500])
    except Exception as e:
        traceback.print_tb(e.__traceback__)
        print(e)
    finally:
        channel.basic_ack(method.delivery_tag)


service = RabbitService('127.0.0.1', RabbitConfig.PORT,
                        RabbitConfig.USER, RabbitConfig.PASSWORD)
service.add_topic(MainTopic.MAIN)
service.add_topic(MainTopic.ERROR)
service.add_topic(ProviderConfig.TOPIC_NAME)
service.add_exchange(MainTopic.MAIN, 'topic')
service.add_exchange(MainTopic.ERROR, 'topic')
service.add_exchange(ProviderConfig.TOPIC_NAME, 'topic')

print(f"[*] Starting Consuming {MainTopic.MAIN}")
service.start_consuming(MainTopic.MAIN, callback_func=on_message_received)

DEFAULT_MESSAGE = {
    "modelLabel": "",
    "modelId": "",
    "classifier": "",
    "options": [],
    "features": [[]],
    "labels": [],
    "serializedModelData": {
        'model': "",
        'attribute': "",
        'labels': [],
        'distributions': []
    },
    "metrics": ""
}

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

x, y = make_classification(n_samples=20, n_features=5)
MESSAGE_TRAIN = {
    "modelLabel": RequestStatus.TRAIN,
    "modelId": "123",
    "features": x.tolist(),
    "labels": y.tolist(),
    "serializedModelData": {
        "model": serialize_model(RandomForestClassifier()),
    },
}

clf = RandomForestClassifier()
clf = clf.fit(x, y)
MESSAGE_PREDICT = {
    "modelLabel": RequestStatus.PREDICT,
    "modelId": "123",
    "features": x[:4].tolist(),
    "serializedModelData": {
        "model": serialize_model(clf),
    }
}

deep_update(DEFAULT_MESSAGE, MESSAGE_CREATE)
service.send_message(ProviderConfig.TOPIC_NAME, DEFAULT_MESSAGE)
print('Create model')

deep_update(DEFAULT_MESSAGE, MESSAGE_TRAIN)
service.send_message(ProviderConfig.TOPIC_NAME, DEFAULT_MESSAGE)
print('Train model')

deep_update(DEFAULT_MESSAGE, MESSAGE_PREDICT)
service.send_message(ProviderConfig.TOPIC_NAME, DEFAULT_MESSAGE)
print('Model predict')

print(f"[*] Starting Consuming {MainTopic.MAIN}")
service.start_consuming(MainTopic.MAIN, callback_func=on_message_received)
