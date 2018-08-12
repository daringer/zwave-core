import functools
from enum import IntEnum
import urllib

from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from flask_restful import reqparse
from flask import abort
from flask import url_for

#import openzwave
#from openzwave.node import ZWaveNode
#from openzwave.value import ZWaveValue
#from openzwave.scene import ZWaveScene
#from openzwave.controller import ZWaveController
#from openzwave.network import ZWaveNetwork
#from openzwave.option import ZWaveOption

#from pydispatch import dispatcher

###### own
from parsers import opt_parse

#from signals import net_signals

from zwave_cls import ZWave


name = "Z-WaveCentral"

app = Flask(name) # __name__
api = Api(app)

# 
#def api_route(self, *args, **kwargs):
#    def wrapper(cls):
#        self.add_resource(cls, *args, **kwargs)
#        return cls
#    return wrapper



@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": 404, "message": "not found", "url": request.url})

@app.errorhandler(403)
def not_allowed(error):
    return jsonify({"error": 403, "message": "not allowed"})

@app.errorhandler(414)
def not_ready(error):
    return jsonify({"error": 414, "message": "not ready"})



### woho, brain-shrinking 8-liner:
### wrapping decorator alias its arguments based on the decorating method/alias name
class _rest:
  def __getattr__(self, key):
      return self._wrap(key)
  def _wrap(self, method):
      @functools.wraps(app.route)
      def func(*v, **kw):
          kw["methods"] = [method.upper()]
          return app.route(*v, **kw)
      return func
rest = _rest()



#def abort_unknown_uid(ctrl_uid):
#    abort(404, message="Todo {} doesn't exist".format(todo_id))

def build_dct_from(obj, names):
  return dict( (name, getattr(obj, name)) for name in names )

class NetState(IntEnum):
    stopped   = 0
    failed    = 1
    resetted  = 3
    started   = 5
    awaked    = 7
    ready     = 10

def get_member(src, attr_name, args):
    obj = getattr(src, attr_name)
    kw = {}
    if callable(obj):
        for key, val in args.items():
            if val.startswith("[int]"):
                kw[key] = int(val[5:])
            elif val.startswith("[float]"):
                kw[key] = float(val[7:])
            else:
                kw[key] = val
        return obj(**kw)
    return obj

zwave = ZWave(abort)

class Options(Resource):
    def get(self):
        return {"options": dict(zwave.raw_opts.items()) }
    def patch(self):
        zwave.update_options(opt_parse.parse_args(strict=True))
        return {"options-state": "editable", "options": dict(zwave.raw_opts.items()) }
    def post(self):
        zwave.set_options()
        return {"options-state": "locked",   "options": dict(zwave.raw_opts.items()) }
    def delete(self):
        zwave.clear_options()
        return {"options-state": "empty",    "options": dict(zwave.raw_opts.items()) }

#@rest.get("/toc")
#def list_routes():
#    output = []
#    for rule in app.url_map.iter_rules():
#
#        options = {}
#        for arg in rule.arguments:
#            print (arg)
#            options[arg] = "[{}]".format(arg)
#        
#        methods = ','.join(rule.methods)
#        url = url_for(rule.endpoint, **options)
#        line = urllib.parse.unquote("{:<35s} {:<40s} {:<20s}". \
#            format(url, methods, rule.endpoint))
#        output.append(line)
#    return jsonify(list(sorted(output)))

####
#### NETWORK
####
@rest.get("/net/signals")
def list_signals():
    return jsonify(net_signals)


@rest.get("/net")
def netinfo(member=None):
    if zwave.net is None:
        abort(414)
    return jsonify(zwave.net.to_dict())

@rest.post("/net/action/<string:member>")
def netaction(member):
    if (zwave.net is None and member != "start") and not hasattr(zwave.net, member):
        abort(404)
  
    ret = zwave.start() if member == "start" else \
        get_member(zwave.net, member, request.args)
    
    if zwave.net is None:
      abort(414)
  
    return jsonify({"returned": ret,
        "network-state": NetState(zwave.net.state).name,
        "executed-member": member,
        "network": zwave.net.to_dict()})

@rest.post("/net/ctrl/action/<string:member>")
def ctrlaction(member, ctrl_idx=0):
    idx = ctrl_idx
    ctrl = zwave.ctrl[idx]
    if not zwave.net:
        abort(414)
    if not hasattr(ctrl, member):
        abort(404)

    ret = get_member(ctrl, member, request.args)
    if isinstance(ret, set): 
        ret = list(ret)
    return jsonify({"returned": ret, 
        "ctrl-name": ctrl.name,
        "executed-action": member,
        "controller": ctrl.to_dict()})

@rest.get("/nodes")
def nodelist():
    if not zwave.net:
        abort(414)       
    return jsonify({ "nodes": [node.to_dict() for nid, node in zwave.net.nodes.items()] })

class Node(Resource):
    def get(self, node_id):      
        return {"node-state": dict(zwave[node_id].to_dict()) }
    def patch(self, node_id):
        return {"node-state": dict(zwave[node_id].to_dict()) }
    def post(self, node_id):
        return {"node-state": dict(zwave[node_id].to_dict()) }
    def delete(self, node_id):
        return {"node-state": dict(zwave[node_id].to_dict()) }


class NodeConfig(Resource):
    def get(self, node_id):
        return {"node-state": dict(zwave[node_id].to_dict()) }
    def patch(self, node_id):
        return {"node-state": dict(zwave[node_id].to_dict()) }
    def post(self, node_id):
        return {"node-state": dict(zwave[node_id].to_dict()) }
    def delete(self, node_id):
        return {"node-state": dict(zwave[node_id].to_dict()) }


api.add_resource(Options,          "/net/opts")
api.add_resource(Node,             "/node/<int:node_id>")
api.add_resource(NodeConfig,       "/node/<int:node_id>/config")



if __name__ == '__main__':
    app.run(debug=True)
