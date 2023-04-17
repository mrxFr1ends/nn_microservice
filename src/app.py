import os, sys
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from datetime import datetime
import json
from config import Provider, MainTopic
from rabbit_service import RabbitService
from classificator import Classificator
from request_handlers import request_handler_map

def register_provider():
    message = {
        "providerName": Provider.NAME,
        "topicName": Provider.TOPIC_NAME,
        "algorithms": [{
            "algName": alg,
            "hyperparameters": [{
                'descriptionFlag': p[0],
                'description': p[1]
            } for p in Classificator.get_hyperparams(alg).items()]
        } for alg in Classificator.get_algorithms()]
    }
    service.send_message(MainTopic.MAIN, message)
    print(f"[+] Algorithms was sent to '{MainTopic.MAIN}' topic")


def send_error_message(model_id, info, exp):
    message = {
        "modelId": model_id,
        "errorType": type(exp).__name__,
        "errorMessage": info + " " + str(exp),
        "localDateTime": str(datetime.now())
    }
    service.send_message(MainTopic.ERROR, message)
    print(f"    [+] Error was sent to '{MainTopic.ERROR}' topic")


def try_deserialize_request(request):
    try:
        req = json.loads(request)
        _, _ = req['modelLabel'], req['modelId']
        return req
    except Exception as exp:
        print("    [x] Invalid Request")
        print(f"    {type(exp).__name__}: {exp}")
        return None


def handle_request(req, handler, res_status, required_keys):
    req = {**req, **handler(*[req[_] for _ in required_keys])}
    req['modelLabel'] = res_status
    service.send_message(MainTopic.MAIN, req)
    print(f"    [+] Response '{res_status}' was sent to '{MainTopic.MAIN}' topic")


def on_message_received(ch, method, properties, request):
    print("[+] Received new message")
    if (req := try_deserialize_request(request)) is None:
        return

    model_label = req['modelLabel']
    print(f"    [!] Request type: {model_label}")
    if model_label not in request_handler_map:
        print(f"    [x] Invalid request type '{model_label}'")
        return

    try:
        handle_request(req, *request_handler_map[model_label].values())
    except Exception as exp:
        print(f"    [x] {type(exp).__name__}: {exp}")
        send_error_message(req['modelId'], f"Status: '{model_label}'", exp)


if __name__ == '__main__':
    service = RabbitService()
    register_provider()
    print("[*] Starting Consuming")
    service.start_consuming(callback_func=on_message_received)
