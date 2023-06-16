
def find_item(list_dict, cb: lambda x: True) -> (dict, int):
  for (idx, item) in enumerate(list_dict):
    if cb(item):
      return item, idx

  return {}, -1