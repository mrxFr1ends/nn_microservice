from sklearn.ensemble import RandomForestClassifier
import pickle, base64, json, zlib

_class = globals()['RandomForestClassifier']
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

def print_full_size_json_data(title, data):
  print(title, len(json.dumps([data, hyperparams], separators=(',', ':'))))

clf = RandomForestClassifier()
clf.fit([[1,2,3],[4,5,6],[7,8,9]], [0, 1, 1])

clf_dump = pickle.dumps(clf)
clf_b64 = base64.b64encode(clf_dump)
clf_compress_dump = zlib.compress(clf_dump)
clf_compress_b64 = zlib.compress(clf_b64)

clf_b64_2_dump = base64.b64encode(clf_compress_dump)
clf_b64_2_b64 = base64.b64encode(clf_compress_b64)
clf_comp_2_dump = zlib.compress(clf_b64_2_dump)
clf_comp_2_b64 = zlib.compress(clf_b64_2_b64)

print("Size of dump:", len(clf_dump))
print("Size of b64 dump", len(clf_b64))
print_full_size_json_data("Default dump (list):", list(clf_dump))
print_full_size_json_data("Default dump b64 (str):", str(clf_b64))
print_full_size_json_data("Compress dump (list):", list(clf_compress_dump))
print_full_size_json_data("Compress b64 (list)", list(clf_compress_b64))
print_full_size_json_data("Compress dump to b64 (str)", str(clf_b64_2_dump))
print_full_size_json_data("Compress b64 to b64 (str)", str(clf_b64_2_b64))
print_full_size_json_data("Compress second dump (list)", list(clf_comp_2_dump))
print_full_size_json_data("Compress second b64 (list)", list(clf_comp_2_b64))