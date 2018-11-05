from openzwave.object import ZWaveException
from openzwave.node import ZWaveNode
from openzwave.value import ZWaveValue
from openzwave.network import ZWaveNetwork
from openzwave.controller import ZWaveController
from openzwave.option import ZWaveOption

def listify(it_or_not):
    """Less aggressive `to_json()` variant, which mainly handles sets"""
    if isinstance(it_or_not, set):
        return [x for x in it_or_not]
    return it_or_not

def to_json(obj, max_depth=10, cur_depth=0):
    """Recurse through `obj` to jsonify non-jsonifyable data-types (not cycle safe!)"""
    if cur_depth > max_depth:
      return "{...}"

    if isinstance(obj, dict):
        out = {}
        for key, val in obj.items():
          if key == "value_id":
              out[key] = str(val)
          else:
              out[key] = to_json(val)
        return out

    elif isinstance(obj, (ZWaveValue, ZWaveNode, ZWaveNetwork, ZWaveOption, ZWaveController)):
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
        return [to_json(sub_obj, max_depth=max_depth, cur_depth=cur_depth + 1) for sub_obj in obj]

    elif isinstance(obj, (int, str, float, complex, bool, type(None))):
        if isinstance(obj, int) and obj > 2**53-1:
          return str(obj)
        return obj

    else:
        return "[cls: {}]".format(obj.__class__.__name__)
    return obj
