import functools
from enum import IntEnum
import urllib

from flask import Flask, jsonify, request, Response
from flask_restful import Resource, Api
from flask_restful import reqparse
from flask import abort
from flask import url_for

from flask_socketio import SocketIO, emit

from jinja2 import Template, Environment, PackageLoader, select_autoescape, BaseLoader


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

app.config['SECRET_KEY'] = "meissna_geheim"
socketio = SocketIO(app)

# 
#def api_route(self, *args, **kwargs):
#    def wrapper(cls):
#        self.add_resource(cls, *args, **kwargs)
#        return cls
#    return wrapper

###
### socket-io -> websocket for signal-triggered browser updates
###

#@socketio.on("foo", namespace="/websocket")
#def event_msg(message):
#    emit("event_msg", {"data": message["data"]})

#@socketio.on("my broadcast event", namespace="/test")
#def test_message(message):
#    emit("my response", {"data": message["data"]}, broadcast=True)

@socketio.on("connect", namespace="/websocket")
def test_connect():
    #emit("my response", {"data": "Connected"})
    pass

@socketio.on("disconnect", namespace="/websocket")
def test_disconnect():
    #print("Client disconnected")
		pass


###
### Error handling
### @todo: find some neat scheme to have consistent error-handlers
###

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": 404, "message": "not found", "url": request.url})

@app.errorhandler(403)
def not_allowed(error):
    return jsonify({"error": 403, "message": "not allowed"})

@app.errorhandler(414)
def not_ready(error):
    return jsonify({"error": 414, "message": "not ready"})

@app.errorhandler(415)
def no_controller(error):
    return jsonify({"error": 415, "message": "no controller found"})



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
    if callable(obj):
        kw = {}
        for key, val in args.items():
            if val.startswith("[int]"):
                kw[key] = int(val[5:])
            elif val.startswith("[float]"):
                kw[key] = float(val[7:])
            elif val.startswith("[bool]"):
                kw[key] = val[6:].lower() == "true"
            else:
                kw[key] = val
        return obj(**kw)
    return obj

zwave = ZWave(abort)


###
### webpage(s)
### 

@rest.get("/get_emit")
def myemit():
    emit("event_msg", "hello my websocket mesage")



@app.route("/frontend/css/<string:name>")
def frontend_css(name):
    with open("{}.css".format(name)) as fd:
        tmpl = Environment(loader=BaseLoader).from_string(fd.read())
    return Response(tmpl.render(), mimetype="text/css")

@app.route("/frontend/js/<string:name>")
def frontend_js(name):
    with open("js/{}.js".format(name)) as fd:
        tmpl = Environment(loader=BaseLoader).from_string(fd.read())
    return Response(tmpl.render(), mimetype="text/javascript")

@app.route("/frontend")
def frontend():
    with open("frontend.html") as fd:
        tmpl = Environment(loader=BaseLoader).from_string(fd.read())
    return tmpl.render()

###
### options
###

class Options(Resource):
    def get(self):
        return {"options": dict(zwave.raw_opts.items()) }
    def patch(self):
        zwave.update_options(opt_parse.parse_args(strict=True))
        return {"options-state": "editable", "options": dict(zwave.raw_opts.items()) }
    def post(self):
        zwave.update_options(opt_parse.parse_args(strict=True))
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
    from signals import net_signals
    return jsonify(net_signals)

@rest.get("/net/signals/latest/<int:num>")
def latest_signals(num):
    return jsonify(list(map(lambda x: (x[0], str(x[1]), x[2]), zwave.signals[-num:])))

@rest.get("/net")
def netinfo():
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

@rest.get("/net/actions")
def available_net_actions():
    if (zwave.net is None and member != "start") and not hasattr(zwave.net, member):
        abort(404)
  
    if zwave.net is None:
      abort(414)
    
    return jsonify(["heal", "start", "stop", "home_id", "is_ready", "nodes_count", "get_scenes", 
        "scenes_count", "test", "sleeping_nodes_count", "state", "write_config"])


@rest.get("/net/ctrl/actions")
def available_ctrl_actions(ctrl_idx=0):
    ctrl = zwave.ctrl[ctrl_idx] if len(zwave.ctrl) > ctrl_idx else None
    if ctrl is None:
        abort(415)
    if not zwave.net:
        abort(414)

    return jsonify(["start", "stop", "add_node", "assign_return_route", "cancel_command", 
            "capabilities", "device", "is_primary_controller", "library_config_path", 
            "library_description", "library_type_name", "library_user_path", "library_version", 
            "name", "node", "node_id", "options", "owz_library_version", 
            "python_library_config_version", "stats"])

@rest.post("/net/ctrl/action/<string:member>")
def ctrlaction(member, ctrl_idx=0):
    ctrl = zwave.ctrl[ctrl_idx] if len(zwave.ctrl) > ctrl_idx else None
    if ctrl is None:
        abort(415)
    if not zwave.net:
        abort(414)
    if not hasattr(ctrl, member):
        abort(404)

    ret = get_member(ctrl, member, request.args)
    if isinstance(ret, set): 
        ret = list(sorted(ret))
    return jsonify({"returned": ret, 
        "ctrl-name": ctrl.name,
        "executed-action": member,
        "controller": ctrl.to_dict()})

@rest.get("/nodes")
def nodelist():
    if not zwave.net:
        abort(414)       
    return jsonify([[
            { "node_id": nid, "name": node.name, "product_type": node.product_type, 
              "product_name": node.product_name }
        ] for nid, node in zwave.net.nodes.items() ] )


@rest.get("/node/<int:node_id>/values")
def node_values(node_id):
    return jsonify(zwave[node_id].values_to_dict())

class Node(Resource):
    def get(self, node_id):      
        return dict(zwave[node_id].to_dict())
    def patch(self, node_id):
        node = zwave[node_id]
        for key, val in request.args.items():
            if key in ["name", "location", "product_name", "manufacturer_name"]:
                node.set_field(key, val)
            else:
                abort(403)
        return dict(node.to_dict())
    #def post(self, node_id):
    #    return dict(zwave[node_id])
    #def delete(self, node_id):
    #    return dict(zwave[node_id])

class NodeConfig(Resource):
    def get(self, node_id):
        return dict(zwave[node_id].to_dict())
    def patch(self, node_id):
        return dict(zwave[node_id].to_dict())
    def post(self, node_id):
        return dict(zwave[node_id].to_dict())
    def delete(self, node_id):
        return dict(zwave[node_id].to_dict())

class NodeValue(Resource):
    def get(self, node_id, value_id):
        return zwave[node_id].values_to_dict()[value_id]
    def post(self, node_id, value_id):
        return zwave[node_id].values_to_dict()[value_id]

api.add_resource(Options,          "/net/opts")
api.add_resource(Node,             "/node/<int:node_id>")
api.add_resource(NodeConfig,       "/node/<int:node_id>/config")
api.add_resource(NodeValue,        "/node/<int:node_id>/value/<int:value_id>")

if __name__ == '__main__':
    #app.run(debug=True)
    socketio.run(app, debug=True)
