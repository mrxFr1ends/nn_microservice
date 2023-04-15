from sklearn.utils import all_estimators
import pickle
from colorama import Fore, init
init()

def deserialize_model(serialized_model):
  return pickle.loads(bytes(serialized_model))

def serialize_model(model):
  return list(pickle.dumps(model))

class ColorPrint:
  DEFAULT_SPACES = 0
  @staticmethod
  def print(icon, message, spaces=DEFAULT_SPACES):
    print(f"{' ' * spaces}{icon} {message}")
  @staticmethod
  def print_fail(message, spaces=DEFAULT_SPACES):
    ColorPrint.print(f'{Fore.RED}[x]{Fore.RESET}', message, spaces)
  @staticmethod
  def print_success(message, spaces=DEFAULT_SPACES):
    ColorPrint.print(f'{Fore.GREEN}[+]{Fore.RESET}', message, spaces)
  @staticmethod
  def print_info(message, spaces=DEFAULT_SPACES):
    ColorPrint.print(f'{Fore.YELLOW}[!]{Fore.RESET}', message, spaces)
  @staticmethod
  def print_load(message, spaces=DEFAULT_SPACES):
    ColorPrint.print(f'{Fore.CYAN}[*]{Fore.RESET}', message, spaces)

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