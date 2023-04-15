from sklearn.ensemble import (
  AdaBoostClassifier, 
  BaggingClassifier, 
  ExtraTreesClassifier, 
  GradientBoostingClassifier, 
  HistGradientBoostingClassifier, 
  RandomForestClassifier, 
  StackingClassifier, 
  VotingClassifier
)
from sklearn.linear_model import (
  LogisticRegression, 
  LogisticRegressionCV, 
  PassiveAggressiveClassifier, 
  Perceptron, 
  RidgeClassifier,
  RidgeClassifierCV, 
  SGDClassifier
)
from sklearn.naive_bayes import (
  BernoulliNB, 
  CategoricalNB, 
  ComplementNB, 
  GaussianNB, 
  MultinomialNB
)
from sklearn.multiclass import (
  OneVsOneClassifier, 
  OneVsRestClassifier, 
  OutputCodeClassifier
)
from sklearn.neighbors import (
  KNeighborsClassifier, 
  NearestCentroid, 
  RadiusNeighborsClassifier
)
from sklearn.svm import (
  LinearSVC, 
  NuSVC, 
  SVC
)
from sklearn.multioutput import ClassifierChain, MultiOutputClassifier
from sklearn.tree import DecisionTreeClassifier, ExtraTreeClassifier
from sklearn.semi_supervised import LabelPropagation, LabelSpreading
from sklearn.discriminant_analysis import (
  LinearDiscriminantAnalysis,
  QuadraticDiscriminantAnalysis
)
from sklearn.calibration import CalibratedClassifierCV
from sklearn.dummy import DummyClassifier
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.neural_network import MLPClassifier

from sklearn.utils import all_estimators

algorithms = None

def get_algorithms():
  global algorithms
  if algorithms is not None:
    return algorithms
  estimators = all_estimators(type_filter='classifier')
  algorithms = [class_.__name__ for _, class_ in estimators]
  return algorithms

def get_hyperparams(model_name):
  _class = globals()[model_name]
  hyperparams = _class._get_param_names()
  count_params = len(hyperparams)
  params_info = {}
  iter = 0
  for row in _class.__doc__.split('\n'):
    for param in hyperparams:
      if row.startswith(f'    {param} : '):
        params_info[param] = ' '.join(row[row.find(': ') + 2:].split())
        iter += 1
        break
    if iter == count_params:
      break
  # [print(f'{k}\n╚══ {v}\n') for k, v in params_info.items()]
  return params_info

def create(model_name, params):
  return globals()[model_name](**params)

def train(model, X, y):
  clf = model.fit(X, y)
  feature_importances = getattr(clf, 'feature_importances_', None)
  return clf, feature_importances.tolist()

def predict(model, X):
  predict_y = model.predict(X).tolist()
  predict_proba = model.predict_proba(X).tolist() if hasattr(model, 'predict_proba') else None
  return predict_y, predict_proba

# algorithms = ['AdaBoostClassifier', 'BaggingClassifier', 'BernoulliNB', 'CalibratedClassifierCV', 'CategoricalNB', 'ClassifierChain', 'ComplementNB', 'DecisionTreeClassifier', 'DummyClassifier', 'ExtraTreeClassifier', 'ExtraTreesClassifier', 'GaussianNB', 'GaussianProcessClassifier', 'GradientBoostingClassifier', 'HistGradientBoostingClassifier', 'KNeighborsClassifier', 'LabelPropagation', 'LabelSpreading', 'LinearDiscriminantAnalysis', 'LinearSVC', 'LogisticRegression', 'LogisticRegressionCV', 'MLPClassifier', 'MultiOutputClassifier', 'MultinomialNB', 'NearestCentroid', 'NuSVC', 'OneVsOneClassifier', 'OneVsRestClassifier', 'OutputCodeClassifier', 'PassiveAggressiveClassifier', 'Perceptron', 'QuadraticDiscriminantAnalysis', 'RadiusNeighborsClassifier', 'RandomForestClassifier', 'RidgeClassifier', 'RidgeClassifierCV', 'SGDClassifier', 'SVC', 'StackingClassifier', 'VotingClassifier']