import config as cfg
from rabbit_service import RabbitService
from classificator import Classificator
from request_handlers import request_handler_map
import datetime
import json

def register_provider():
  message = {
    "providerName": cfg.PROVIDER_NAME,
    "topicName": cfg.TOPIC_NAME,
    "algorithms": [{
      "algName": alg, 
      "hyperparameters": [{
        'descriptionFlag': p[0], 
        'description': p[1]
      } for p in Classificator.get_hyperparams(alg).items()]
    } for alg in Classificator.get_algorithms()]
  }
  service.send_message(cfg.MAIN_TOPIC, message)
  print(f"[+] Algorithms was sent to '{cfg.MAIN_TOPIC}' topic")

def send_error_message(modelId, info, exp):
  message = {
    "modelId": modelId,
    "errorType": type(exp).__name__,
    "errorMessage": info + " " + str(exp),
    "localDateTime": str(datetime.datetime.now())
  }
  service.send_message(cfg.ERROR_TOPIC, message)
  print(f"    [+] Error was sent to '{cfg.ERROR_TOPIC}' topic")

def try_deserialize_request(request):
  try:
    req = json.loads(request)
    _, _ = req['modelLabel'], req['modelId']
    return req
  except Exception as e:
    print("    [x] Invalid Request")
    print(f"    {type(e).__name__}: {e}")
    return None

def handle_request(req, handler, res_status, required_keys):
  req = {**req, **handler(*[req[_] for _ in required_keys])}
  req['modelLabel'] = res_status
  service.send_message(cfg.MAIN_TOPIC, req)
  print(f"    [+] Response '{res_status}' was sent to '{cfg.MAIN_TOPIC}' topic")

def on_message_received(ch, method, properties, request):
  print("[+] Received new message")
  if (req := try_deserialize_request(request)) is None:
    return 
  
  modelLabel = req['modelLabel']
  print(f"    [!] Request type: {modelLabel}")
  if modelLabel not in request_handler_map:
    print(f"    [x] Invalid request type '{modelLabel}'")
    return 
  
  try:
    handle_request(req, *request_handler_map[modelLabel].values())
  except Exception as e:
    print(f"    [x] {type(e).__name__}: {e}")
    send_error_message(req['modelId'], f"Status: '{modelLabel}'", e)

if __name__ == '__main__':
  service = RabbitService()
  register_provider()
  print("[*] Starting Consuming")
  service.start_consuming(callback_func=on_message_received)