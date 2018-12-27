from openzwave.object import ZWaveException
from openzwave.node import ZWaveNode
from openzwave.value import ZWaveValue
from openzwave.network import ZWaveNetwork
from openzwave.controller import ZWaveController
from openzwave.option import ZWaveOption



class ItemsToAttrs:
    def __init__(self, data_dct):
        self._data_dct = data_dct

    def __getattr__(self, key):
        out = self._data_dct[key]
        if isinstance(out, dict):
            return self.__class__(out)
        return out


def listify(it_or_not):
    """Less aggressive `to_json()` variant, which mainly handles sets"""
    if isinstance(it_or_not, set):
        return [x for x in it_or_not]
    return it_or_not

def to_json(obj, max_depth=10, cur_depth=0):
    """Recurse through `obj` to jsonify non-jsonifyable data-types (not cycle safe!)"""
    #print (f"START-JSON: {type(obj)} depth: {cur_depth} {obj} ")
    if cur_depth > max_depth:
        #print (f"TO-JSON too deep!: {obj}")
        return "{...}"

    if isinstance(obj, dict):
        out = {}
        for key, val in obj.items():
          if key == "value_id":
              out[key] = str(val)
          else:
              #print (f"descent dict key: {key}")
              out[key] = to_json(val)
        return out

    elif isinstance(obj, (ZWaveValue, ZWaveNode, ZWaveNetwork, ZWaveOption, ZWaveController)):
        print ("#"*50)
        print ("#"*50)
        print (f"NON-JSON: {type(obj)} depth: {cur_depth} {obj} ")
        print ("#"*50)
        print ("#"*50)
        #if isinstance(obj, (ZWaveValue, ZWaveNode, ZWaveNetwork, ZWaveController)):
        if isinstance(obj, (ZWaveValue, ZWaveNode)):
            dct = obj.to_dict()
            x = dict((k, listify(dct[k])) for k in dct.keys())
            if "value_id" in x:
                x["value_id"] = str(x["value_id"])
            return x
        else:
            return obj.__class__.__name__

    elif isinstance(obj, (tuple, list, frozenset, set)):
        #print (f"TO-JSON (tup, li, fros, se): {obj}")
        return [to_json(sub_obj, max_depth=max_depth, cur_depth=cur_depth + 1) for sub_obj in obj]

    elif isinstance(obj, (int, str, float, complex, bool, type(None))):
        #print (f"TO-JSON (PoD): {obj}")
        if isinstance(obj, int) and obj > 2**53-1:
          return str(obj)
        return obj

    else:
        return "[cls: {}]".format(obj.__class__.__name__)
    return obj
