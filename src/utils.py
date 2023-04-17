from sklearn.utils import all_estimators
import pickle


def deserialize_model(serialized_model):
    return pickle.loads(bytes(serialized_model))


def serialize_model(model):
    return list(pickle.dumps(model))


def get_algorithms(print_imports=False):
    estimators = all_estimators(type_filter='classifier')
    algorithms = []
    for name, class_ in estimators:
        module_name = str(class_).split("'")[1].split(".")[1]
        class_name = class_.__name__
        algorithms.append(class_name)
        if print_imports:
            print(f'from sklearn.{module_name} import {class_name}')
    return algorithms
