import functools
import os
import urllib
from enum import IntEnum
from time import time
from uuid import uuid4
import json

import eventlet
from eventlet.queue import Empty, Full, Queue
from eventlet.semaphore import Semaphore as Lock
from flask import Flask, Response, abort, jsonify, request, url_for, make_response
from flask_restful import Api, Resource, reqparse
from flask_socketio import SocketIO, emit, send
from jinja2 import (BaseLoader, Environment, PackageLoader, Template,
                    select_autoescape)

from openzwave.object import ZWaveException
from openzwave.node import ZWaveNode
from openzwave.value import ZWaveValue

##
## monkeypatch UID as unique id: uid == id_on_network
ZWaveValue.uid = property(lambda self: self.id_on_network.replace(".","_"))
## @TODO: you don't think this is a permanent solution, right?
##


from openzwave.network import ZWaveNetwork
from openzwave.controller import ZWaveController
from openzwave.option import ZWaveOption

from enums import NetState, OptionState
###### own
from parsers import nodes_parse, opt_parse, value_parse
from zwave_cls import ZWave, get_member


app = Flask(__name__)
api = Api(app)


def to_json(obj, max_depth=10, cur_depth=0):
    """Recurse through `obj` to jsonify non-jsonifyable data-types (not cycle safe!)"""
    if cur_depth > max_depth:
      return "[...]"

    if isinstance(obj, dict):
        #keys = [k for k in obj.keys() if (not isinstance(k, str) or not k.startswith("_"))]
        #vals = map(lambda x: to_json(x, max_depth=max_depth, cur_depth=cur_depth + 1), obj.values())
        #return dict(zip(keys, vals))
        out = {}
        for key, val in obj.items():
          if key == "value_id":
              out[key] = str(val)
          else:
              out[key] = to_json(val) #to_json(val, max_depth=max_depth, cur_depth=cur_depth+1)
          #print ("TO_JSON", key, val)
        #print (out)
        return out
    elif isinstance(obj, (ZWaveValue, ZWaveNode, ZWaveNetwork, ZWaveOption, ZWaveController)):
        if isinstance(obj, ZWaveValue):
            return to_json(obj.to_dict(), max_depth=max_depth, cur_depth=cur_depth+1)
        elif isinstance(obj, ZWaveNode):
            return to_json(obj.to_dict(), max_depth=max_depth, cur_depth=cur_depth+1)
        else:
            return obj.__class__.__name__
            #print("JSON ZWAVEVAL", obj.to_dict())

        #return dict((key, to_json(val, max_depth=max_depth, cur_depth=cur_depth)) \
        #            for key, val in obj.to_dict().items() \
        #            if (not isinstance(key, str) or not key.startswith("_")))
    elif isinstance(obj, (tuple, list, frozenset, set)):
        return [to_json(sub_obj, max_depth=max_depth, cur_depth=cur_depth + 1) for sub_obj in obj]
    elif isinstance(obj, (int, str, float, complex, bool, type(None))):
        if isinstance(obj, int) and obj > 2**53-1:
          return str(obj)
        return obj
    else:
        return "[cls: {}]".format(obj.__class__.__name__)
    return obj

@api.representation('application/json')
def output_json(data, code, headers=None):
    """overwrite application/json based responses using this function"""
    data = to_json(data)
    resp = make_response(json.dumps(data), code)
    resp.headers.extend(headers or {})
    return resp

#app.config['SECRET_KEY'] = "meissna_geheim"

socketio = SocketIO(app, async_mode="eventlet")

#SocketIO.
#socketio = SocketIO.AsyncServer(async_mode="aiohttp")
#socketio = SocketIO(app, async_mode="threading")
#socketio = SocketIO(app, async_mode="gevent")

#@app.after_request
#def no_caching_header(r):
#    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
#    r.headers["Pragma"] = "no-cache"
#    r.headers["Expires"] = "0"
#    r.headers['Cache-Control'] = 'public, max-age=0'
#    return r

#def api_route(self, *args, **kwargs):
#    def wrapper(cls):
#        self.add_resource(cls, *args, **kwargs)
#        return cls
#    return wrapper

thread = None
thread_lock = Lock()


@socketio.on("connect", namespace="/websocket")
def io_connect():
    emit(
        "message", {"msg": "Hello World (from websocket server)"},
        namespace="/websocket")  #oom="ficken", broadcast=True)

    def consume_queue():
        global sig_queue
        while True:
            try:
                item = sig_queue.get(timeout=5)
                socketio.send(to_json(item), namespace="/websocket")  #, broadcast=True)
            except Empty:
                continue

    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(consume_queue)
    return True


@socketio.on("disconnect", namespace="/websocket")
def io_disconnect():
    emit(
        "message", {"msg": "Goodbye World (from websocket server)"},
        namspace="/websocket")
    return True


###
### (ajax)response creation helper
###
###
class Ajax:
    def __init__(self, data=None, msg=None, err=None, jsonify=False):
        self.jsonify = jsonify

        self._data = {}
        self._msg = msg or None
        self._error = err or None
        if data is not None:
          self._data = data

    @property
    def msg(self, msg):
        return self._msg
    @msg.setter
    def msg(self, msg):
        self._msg = msg

    @property
    def data(self):
        return self._data
    @data.setter
    def data(self, raw_data):
        self._data = raw_data
    def __setitem__(self, data_key, data_val):
        self._data[data_key] = data_val
    def __getitem__(self, data_key):
        return self._data[data_key]

    def set_state(self, which, state):
        self._data.setdefault("states", {})[which] = state
        return self

    def set_err(self, code, msg=None):
        self._error = code
        self.msg = msg
        return self

    def render(self):
      out = {}
      if len(self._data) > 0:
          out["data"] = self._data
      if self._msg:
          out["msg"] = self._msg
      if self._error:
          out["error"] = self._error
      return out if not self.jsonify else jsonify(out)

def ret_ajax(data, msg=None):
    return Ajax(data=data, msg=msg).render()
def ret_jajax(data, msg=None):
    return Ajax(data=data, msg=msg, jsonify=True).render()
def ret_err(code, msg=None):
    return Ajax(err=code, msg=msg).render()
def ret_jerr(code, msg=None):
    return Ajax(err=code, msg=msg, jsonify=True).render()
def ret_msg(msg):
    return Ajax(msg=msg).render()
def ret_jmsg(msg):
    return Ajax(msg=msg, jsonify=True).render()

###
### Error handling
### @todo: find some neat scheme to have consistent error-handlers
###        (i.e., stop abusing http-errorcodes here!)
###
@app.errorhandler(404)
def not_found(error):
    return ret_jerr(404, "not found: {}".format(request.url))

@app.errorhandler(403)
def not_allowed(error):
    return ret_jerr(403, "not allowed")

@app.errorhandler(414)
def not_ready(error):
    return ret_jerr(414, "not ready")

@app.errorhandler(415)
def no_controller(error):
    return ret_jerr(415, "no controller found")


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

#### @todo: find out if the eventlet based websocket is now really working or just by accident!
#### @TODO: those two here have NOOO limits in size!!!! @FIXME
sig_queue = Queue()
#sig_archive = {}

def default_signal_handler(sender, signal, *v, **kw):
    global sig_queue #, sig_archive
    print ("DEFAULT HANDLER START", signal)
    x = {
        "stamp": time(),
        "sender": str(sender),
        "event_type": signal,
        "uuid": uuid4().int % ((2**32)-1)
    }
    #print("PRE WHILE", x["uuid"], signal, kw)
    while True:
        #print ("WHILE SIG HDNL:" , x["uuid"], kw)
        try:
            print (kw)
            if "node" in kw:
                x["node_id"] = kw["node"].node_id
            if "value" in kw:
                x["value"] = kw["value"]
                x["value"].value_id = str(x["value"].value_id)
                x["value_id"] = str(kw["value"].value_id)
                x["data"] = kw["value"].data

            #print ("INSIDE TRY:", x)
                        #if "args" in kw:
            #    x["args"] = str(list(map(str, kw["args"])))
            #if "network" in kw:
            #    x["network"] = kw["network"].state
            #if all((k not in kw) for k in ["node", "value", "args", "network"]):
            #    x["full"] = str(kw)
            #x.update(kw)
            #cpy = dict(x.items())
            #cpy =
            #cpy["data"] = cpy["data"].data
            x.update(kw)
            #"node"] = x
            #el x["network"]
            #el x["value"]
            print ("ENQUEING:",x)
            sig_queue.put(to_json(x, max_depth=3), timeout=5)
            #sig_archive[x["uuid"]] = x
            break
        except Full:
            continue
    return True

###
### (web)page(s)
###
@app.route("/static/<string:path>")
@app.route("/static/js/<string:path>")
def frontend_static(path):
    if not os.path.exists(path):
        if not os.path.exists("js/" + path):
            abort(404)
        else:
            path = "js/" + path

    with open(path) as fd:
        data = fd.read()

    if path.endswith(".js") or path.endswith(".map"):
        return Response(data, mimetype="text/javascript")
    elif path.endswith(".css"):
        return Response(data, mimetype="text/css")
    else:
        return Response(data, mimetype="text/plain")

@app.route("/frontend")
def frontend():
    with open("frontend.html") as fd:
        tmpl = Environment(loader=BaseLoader).from_string(fd.read())
    return tmpl.render()

##
## non static resources
##
class Options(Resource):
    def get(self):
        return to_ajax({"options": dict(zwave.raw_opts.items())})

    def patch(self):
        msg = None
        try:
            zwave.update_options(opt_parse.parse_args(strict=True))
        except ZWaveException as e:
          return Ajax(msg="ZWaveException thrown: {}".format(str(e))) \
              .set_state("options", OptionState.failed).render()

        return Ajax(data=dict(zwave.raw_opts.items())) \
            .set_state("options", OptionState.editable).render()

    def post(self):
        try:
            zwave.update_options(opt_parse.parse_args(strict=True))
        except ZWaveException as e:
            return Ajax(msg="ZWaveException thrown: {}".format(str(e))) \
                .set_state("options", OptionState.failed).render()

        p = zwave.raw_opts.device
        if p is None or not os.path.exists(p) or \
            (not open(p, "rb").readable()) or \
            (not open(p, "wb").writable()):
                print ("bad device path: {}".format(p))
                return ret_err(404, "Could not open zwave serial device: {}".format(p))
        try:
            zwave.set_options()
        except ZWaveException as e:
            return Ajax(msg="ZWaveException thrown: {}".format(str(e))) \
                .set_state("options", OptionState.failed).render()

        return Ajax(data=dict(zwave.raw_opts.items())) \
            .set_state("options", OptionState.locked).render()

    def delete(self):
        try:
            zwave.clear_options()
        except ZWaveException as e:
            return ret_err(404, msg="ZWaveException thrown: {}".format(str(e)))
        return Ajax(data=dict(zwave.raw_opts.items())) \
           .set_state("options", OptionState.empty).render()

###
### "Table of contents"
###
@rest.get("/toc")
def list_routes():
    from random import randint
    output = []
    for rule in app.url_map.iter_rules():
        options = {}
        opt2str = {}
        for arg in rule.arguments:
            if arg in ["num", "node_id", "value_id"]:
                opt2str[arg] = (randint(12331, 32425), "int")
                options[arg] = opt2str[arg][0]
            elif arg in ["member", "path"]:
                opt2str[arg] = (randint(54355, 68684), "string")
                options[arg] = str(opt2str[arg][0])
            else:
                options[arg] = arg
        methods = ','.join(rule.methods)
        url = url_for(rule.endpoint, **options)
        for val, (num, dtype) in opt2str.items():
            url = url.replace(str(num), "<{}:{}>".format(dtype, val))
        line = urllib.parse.unquote("{:<35s} {:<40s} {:<20s}". \
                                    format(url, methods, rule.endpoint))
        output.append(line)
    return ret_jajax(list(sorted(output)))

###
### NETWORK
###
@rest.get("/net/signals")
def list_signals():
    from signals import net_signals
    return ret_jajax([sig[0] for sig in net_signals])

#@rest.get("/net/signals/latest/<int:num>")
#def latest_signals(num):
#    return jsonify(
#        list(map(lambda x: (x[0], str(x[1]), x[2]), zwave.signals[-num:])))

@rest.get("/net")
def netinfo():
    if zwave.net is None:
        abort(414)
    return ret_jajax(zwave.net.to_dict())

@rest.post("/net/action/<string:action>")
def netaction(action):
    if (zwave.net is None
            and action != "start") and not hasattr(zwave.net, action):
        abort(404)

    ret = zwave.start() if action == "start" else \
        get_member(zwave.net, action, request.args)

    if zwave.net is None:
        abort(414)

    return Ajax(data={"returned": ret, "executed": action}, jsonify=True) \
        .set_state("net", NetState(zwave.net.state)).render()

@rest.get("/net/actions")
def available_net_actions():
    if zwave.net is None:
        abort(414)

    return ret_jajax([
        "heal", "start", "stop", "home_id", "is_ready", "nodes_count",
        "get_scenes", "scenes_count", "test", "sleeping_nodes_count", "state",
        "write_config"
    ])


@rest.get("/net/ctrl/actions")
def available_ctrl_actions(ctrl_idx=0):
    ctrl = zwave.ctrl[ctrl_idx] if len(zwave.ctrl) > ctrl_idx else None
    if ctrl is None:
        abort(415)
    if not zwave.net:
        abort(414)

    return ret_jajax([
        "start",
        "stop",
        "add_node",  # "exclude",
        "assign_return_route",
        "cancel_command",
        "capabilities",
        "device",
        "is_primary_controller",
        "library_config_path",
        "library_description",
        "library_type_name",
        "library_user_path",
        "library_version",
        "name",
        "node",
        "node_id",
        "options",
        "owz_library_version",
        "python_library_config_version",
        "stats"
    ])


@rest.post("/net/ctrl/action/<string:action>")
def ctrlaction(action, ctrl_idx=0):
    ctrl = zwave.ctrl[ctrl_idx] if len(zwave.ctrl) > ctrl_idx else None
    if ctrl is None:
        abort(415)
    if not zwave.net:
        abort(414)
    if not hasattr(ctrl, action):
        abort(404)

    ret = get_member(ctrl, action, request.args)
    if isinstance(ret, set):
        ret = list(sorted(ret))
    #return jsonify({
    return ret_jajax({
        "returned": ret,
        "executed": action,
        "controller": ctrl.to_dict()
    })


@rest.get("/nodes")
def nodelist():
    if not zwave.net:
        abort(414)

    ##### @TODO: test() + stats() MISSING!!!


    status_props = ["is_awake", "is_beaming_device", "is_failed", "is_frequent_listening_device",
      "is_info_received", "is_listening_device", "is_locked", "is_ready", "is_routing_device",
      "is_security_device", "is_sleeping", "is_zwave_plus"]
    fields = ["node_id", "name", "query_stage", "location", "type", "specific",
        "product_name", "product_type", "product_id", "query_stage",
        "manufacturer_name", "manufacturer_id"]
    props = ["basic", "capabilities", "command_classes", "device_type", "generic",
        "max_baud_rate", "neighbors", "num_groups", "role", "security", "version"]
    tmp = fields + status_props + props;

    return ret_jajax([to_json(zwave.get_node_details(node_id, tmp)) \
                      for node_id in zwave.net.nodes])

class Node(Resource):
    def get(self, node_id):
        my_groups = {}
        for idx, grp in zwave[node_id].groups.items():
          my_groups[idx] = grp.to_dict()
          my_groups[idx]["index"] = idx
        actions = [
         "assign_return_route",  "heal", "network_update", "neighbor_update",
         "refresh_info", "request_state", "send_information"
        ]
        #for k, v in zwave[node_id].values.items():
        #  print ("VALUE NODEE GET:", k, v, "UID", v.uid)

        #uid2val = dict((v.uid, v) for v in zwave[node_id].values.values())

        return ret_ajax({
            "values": zwave[node_id].values,
            #"uid2val": uid2val,
            "actions": actions,
            "groups": my_groups,
        })

    def patch(self, node_id):
        node = zwave[node_id]
        for key, val in request.args.items():
            if key in ["name", "location", "product_name", "manufacturer_name"]:
                node.set_field(key, val)

        return ret_ajax(dict(node.to_dict()))

@rest.post("/node/<int:node_id>/action/<string:action>")
def node_action(node_id, action):
    node = zwave[node_id]
    getattr(node, action)
    return ret_jmsg(msg="Action: {} sent for node-id: {}".format(action, node_id))

#class NodeGroups(Resource):
#    def get(self, node_id):
#        return self.groups_to_dict()
#
#    def patch(self, node_id):
#        pass

#class NodeConfig(Resource):
#    def get(self, node_id):
#        return ret_ajax(dict(zwave[node_id].to_dict()))
#
#    def post(self, node_id):
#        return ret_ajax(dict(zwave[node_id].to_dict()))

class NodeValue(Resource):
    def get(self, node_id, value_id):
        return ret_ajax(zwave[node_id].values[value_id])
        #return ret_ajax(zwave.get_value_by_uid(uid)[1])

    def post(self, node_id, value_id):
        print ("NODE VALUE SET:", node_id, " VALID: ", value_id)
        data = value_parse.parse_args(strict=True).data
        if data is None:
            print ("no or bad data provided: {}".format(data))
            abort(404)

        #_node_id, val = zwave.get_value_by_uid(uid)

        #try:
        #  print (node_id, uid)
        #  obj = zwave[node_id].values[uid]
        #except KeyError as e:
        #  print ("\n".join(["{1}: {0}".format(zwave[node_id].values[k], k) for k in zwave[node_id].values.keys()]))
        #if node_id is None or value_id is None:

        node_vals = zwave[node_id].values
        if value_id not in node_vals:
            return ret_err(404, msg="ValueID not found: {} node_id: {}".format(value_id, node_id))

        data = zwave[node_id].values[value_id].check_data(data)
        #print ("SEETTTING", val, val.data, "TOOOO:", data)
        if data is None:
            print ("data contents are crap: {}, check_data() failed...".format(data))
            abort(405)
        node_vals[value_id].data = data
                #from IPython import embed
        #embed()
        #val.data = data

        return ret_msg(msg="data for value set successfully")

api.add_resource(Options,       "/net/opts")
api.add_resource(Node,          "/node/<int:node_id>")
#api.add_resource(NodeGroups,    "/node/<int:node_id>/groups")
#api.add_resource(NodeConfig,    "/node/<int:node_id>/config")
api.add_resource(NodeValue,     "/node/<int:node_id>/value/<int:value_id>")


zwave = ZWave(abort, default_signal_handler)

if __name__ == '__main__':
    ####### regular
    #app.run(debug=True)

    ####### eventlet
    app.debug = True
    socketio.run(app, host="127.0.0.1", port=5000, debug=True)

    ####### aiohttp
    #socketio.attach(app)
    #app.run(debug=True)

    ####### eventlet Middleware
    #app = socketio.Middleware(sio)
    #eventlet.wsgi.server(eventlet.listen(('', 8000)), app)

