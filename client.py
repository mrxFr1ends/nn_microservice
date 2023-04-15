import requests as rq
import json
import pickle
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split

HOST = '127.0.0.1'
PORT = '5000'
URL = f'http://{HOST}:{PORT}'

model_info = ["RandomForestClassifier", {"random_state": 0}]
X, y = make_classification(n_samples=1000, n_features=4,
                           n_informative=2, n_redundant=0,
                           random_state=0, shuffle=False)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.01,
                                                    random_state=0, stratify=y)

def load_model(data_array):
  return pickle.loads(bytes(data_array))

def dump_model(model):
  return list(pickle.dumps(model))

def post_request(url, data):
  headers = {"Content-Type": "application/json"}
  return json.loads(rq.post(url, data, headers=headers).content)

def get_algorithms():
  return json.loads(rq.get(f'{URL}/algorithms').content)

def create_model():
  response = post_request(f'{URL}/model/create', json.dumps(model_info))
  return load_model(response[0]), response[1]

def train_model(model, X, y):
  response = post_request(f'{URL}/model/train', json.dumps([dump_model(model), X, y]))
  return load_model(response[0]), response[1]

def model_predict(model, X):
  response = post_request(f'{URL}/model/predict', json.dumps([dump_model(model), X]))
  return response[0], response[1]

algorithms = get_algorithms()

clf, hyperparams = create_model()

# print(f'{"RandomForestClassifier"}:')
# [print(f'{"├" if i<len(hyperparams)-1 else "└"}──{k} : {v}') for i, (k, v) in enumerate(hyperparams.items())]

# print(f'{"RandomForestClassifier"}:')
# max_len_param = max([len(p) for p in hyperparams.keys()])
# [print(f'{"├──"}{k}{"_" * (max_len_param - len(k))}___{v}') for k, v in hyperparams.items()]

# max_len_param = max([len(p) for p in hyperparams.keys()])
# max_len_param_info = max([len(i) for i in hyperparams.values()])
# print(f'{" " * (max_len_param - 4)}Hyperparams:')
# [print(f'{" " * (max_len_param - len(k))}{k} ── {v}') for k, v in hyperparams.items()]

exit(0)

clf, feature_importances = train_model(clf, X_train.tolist(), y_train.tolist())
print("Feature Importances:", feature_importances)

predict_targets, predict_proba = model_predict(clf, X_test.tolist())
print("Predict targets:", predict_targets)
print("Predict proba:", predict_proba)