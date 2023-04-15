from sklearn.ensemble import AdaBoostClassifier, BaggingClassifier, ExtraTreesClassifier, GradientBoostingClassifier, HistGradientBoostingClassifier, RandomForestClassifier, StackingClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression, LogisticRegressionCV, PassiveAggressiveClassifier, Perceptron, RidgeClassifier, RidgeClassifierCV, SGDClassifier
from sklearn.naive_bayes import BernoulliNB, CategoricalNB, ComplementNB, GaussianNB, MultinomialNB
from sklearn.multiclass import OneVsOneClassifier, OneVsRestClassifier, OutputCodeClassifier
from sklearn.neighbors import KNeighborsClassifier, NearestCentroid, RadiusNeighborsClassifier
from sklearn.svm import  LinearSVC, NuSVC, SVC
from sklearn.multioutput import ClassifierChain, MultiOutputClassifier
from sklearn.tree import DecisionTreeClassifier, ExtraTreeClassifier
from sklearn.semi_supervised import LabelPropagation, LabelSpreading
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis, QuadraticDiscriminantAnalysis
from sklearn.calibration import CalibratedClassifierCV
from sklearn.dummy import DummyClassifier
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.utils import all_estimators
from sklearn.model_selection import train_test_split

class Classificator:
  algorithms = None

  @staticmethod
  def get_algorithms():
    if Classificator.algorithms is not None:
      return Classificator.algorithms
    estimators = all_estimators(type_filter='classifier')
    Classificator.algorithms = [class_.__name__ for _, class_ in estimators]
    return Classificator.algorithms

  @staticmethod
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

  @staticmethod
  def create(model_name, params):
    return globals()[model_name](**params)

  @staticmethod
  def train(model, X, y):
    clf = model.fit(X, y)
    feature_importances = getattr(clf, 'feature_importances_', None)
    return clf, feature_importances.tolist()

  def train_model_with_test(model, X, y, test_size=0.33):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=0)
    model, _ = Classificator.train(model, X_train, y_train)
    y_pred, _ = Classificator.predict(model, X_test)
    metrics = [
      accuracy_score(y_test, y_pred),
      precision_score(y_test, y_pred, average="macro"),
      recall_score(y_test, y_pred, average="macro"),
      f1_score(y_test, y_pred, average="macro")
    ]
    return model, metrics

  @staticmethod
  def predict(model, X):
    predict_y = model.predict(X).tolist()
    predict_proba = model.predict_proba(X).tolist() if hasattr(model, 'predict_proba') else None
    return predict_y, predict_proba