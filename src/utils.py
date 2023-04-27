from sklearn.utils import all_estimators
import pickle
import collections.abc


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


def deep_update(source_dict, other):
    stack = [(source_dict, other)]
    while len(stack) > 0:
        source_dict, other = stack.pop(0)
        for key, value in other.items():
            if not isinstance(value, collections.abc.Mapping):
                source_dict[key] = value
            else:
                if key not in source_dict:
                    source_dict[key] = value
                elif not isinstance(source_dict[key], collections.abc.Mapping):
                    source_dict[key] = value
                else:
                    stack.append((source_dict[key], value))


def get_values_deep(source_dict, keys):
    values = []
    for key in keys:
        if not isinstance(key, collections.abc.Mapping):
            values.append(source_dict[key])
        else:
            _key = next(iter(key))
            values.append(*get_values_deep(source_dict[_key], key[_key]))
    return values


def update_values_deep(source_dict, keys, values):
    for index, key in enumerate(keys):
        if not isinstance(key, collections.abc.Mapping):
            source_dict[key] = values[index]
        else:
            _key = next(iter(key))
            update_values_deep(source_dict[_key], key[_key], values[index:])
