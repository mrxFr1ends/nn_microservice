from classificator import Classificator
from utils import serialize_model, deserialize_model
import config as cfg

def create_model(model_name, raw_params):
  params = {}
  for param in raw_params:
    name, value = param.values()
    params[name] = eval(value)
    if name == 'estimator' or name == 'base_estimator':
      params[name] = deserialize_model(params[name])
  model = Classificator.create(model_name, params)
  return {'model': serialize_model(model)}

def train_model(serialized_model, features, labels):
  model = deserialize_model(serialized_model)
  model, metrics = Classificator.train_model_with_test(model, features, labels)
  return {'model': serialize_model(model), 'metrics': metrics}

def model_predict(serialized_model, features):
  model = deserialize_model(serialized_model)
  y_pred, y_proba = Classificator.predict(model, features)
  return {'predictLabels': y_pred, 'prediction': y_proba}

request_handler_map = {
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
    'required_keys': ['model', 'features']
  }
}