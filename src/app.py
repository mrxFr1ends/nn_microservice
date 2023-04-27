from datetime import datetime
import json
import traceback
from config import *
from utils import get_values_deep, update_values_deep
from rabbit_service import RabbitService
from classificator import Classificator as clf


def send_register_message(topic_name):
    algorithms = {alg: [p for p in clf.get_hyperparams(
        alg).items()] for alg in clf.get_algorithms()}
    service.send_message(topic_name, REGISTER_MESSAGE(algorithms))
    print(f"[+] Algorithms was sent to '{topic_name}' topic")


def send_error_message(topic_name, model_id, info, exp):
    args = [model_id, type(exp).__name__, info + " " +
            str(exp), str(datetime.now())]
    service.send_message(topic_name, ERROR_MESSAGE(*args))
    print(f"    [+] Error was sent to '{topic_name}' topic")


def try_deserialize_request(request, required_keys):
    try:
        req = json.loads(request)
        [req[key] for key in required_keys]
        return req
    except Exception as exp:
        print("    [x] Invalid Request")
        print(f"    {type(exp).__name__}: {exp}")
        return None


def handle_request(req, request_handler, comp_request_keys, comp_response_keys, topic_name):
    values = get_values_deep(req, comp_request_keys.values())
    res = request_handler(**dict(zip(comp_request_keys.keys(), values)))
    res = [res] if type(res) is not tuple else res
    update_values_deep(req, list(comp_response_keys.values()), res)
    service.send_message(topic_name, req)
    print(f"    [+] Response was sent to '{topic_name}' topic")


def on_message_received(channel, method, properties, request):
    print("[+] Received new message")
    req = try_deserialize_request(request, ['modelId', 'modelLabel'])
    if req is None:
        return

    model_label = req['modelLabel']
    print(f"    [!] Request type: {model_label}")
    if model_label not in REQUEST_HANDLER_MAP:
        print(f"    [x] Invalid request type '{model_label}'")
        return

    try:
        handle_request(req, **REQUEST_HANDLER_MAP[model_label])
    except Exception as exp:
        print(f"    [x] {type(exp).__name__}: {exp}")
        traceback.print_tb(exp.__traceback__)
        tb_error = ''.join(traceback.format_tb(exp.__traceback__))
        send_error_message(
            MainTopic.ERROR, req['modelId'], f"Status: '{model_label}'", tb_error)
    channel.basic_ack(method.delivery_tag)


if __name__ == '__main__':
    service = RabbitService(
        RabbitConfig.HOST, RabbitConfig.PORT, RabbitConfig.USER, RabbitConfig.PASSWORD)
    service.add_exchange(MainTopic.MAIN, 'topic')
    service.add_exchange(MainTopic.ERROR, 'topic')
    service.add_exchange(ProviderConfig.TOPIC_NAME, 'topic')
    service.add_topic(MainTopic.MAIN)
    service.add_topic(MainTopic.ERROR)
    service.add_topic(ProviderConfig.TOPIC_NAME)
    send_register_message(MainTopic.MAIN)
    print(f"[*] Starting Consuming {ProviderConfig.TOPIC_NAME}")
    service.start_consuming(ProviderConfig.TOPIC_NAME,
                            callback_func=on_message_received)
