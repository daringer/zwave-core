import functools
import os
import urllib
from enum import IntEnum
from time import time
from uuid import uuid4

import eventlet
from eventlet.queue import Empty, Full, Queue
from eventlet.semaphore import Semaphore as Lock
from flask import Flask, Response, abort, jsonify, request, url_for
from flask_restful import Api, Resource, reqparse
from flask_socketio import SocketIO, emit, send
from jinja2 import (BaseLoader, Environment, PackageLoader, Template,
                    select_autoescape)

from enums import NetState
###### own
from parsers import opt_parse
from zwave_cls import ZWave, get_member

#import eventlet
#from eventlet.queue import Queue, Empty, Full
#from threading import Thread, Lock


#import socketio as SocketIO





name = "Z-WaveCentral"

app = Flask(__name__)  # __name__
api = Api(app)

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
    #emit("message", {"msg": "Hello World"}, namespace="/websocket") #oom="ficken", broadcast=True)
    emit(
        "message", {"msg": "Hello World (from websocket server)"},
        namespace="/websocket")  #oom="ficken", broadcast=True)

    def consume_queue():
        global sig_queue
        while True:
            try:
                item = sig_queue.get(timeout=5)
                socketio.send(item, namespace="/websocket")  #, broadcast=True)
                #print ("SENT EVENT: " + str(item))
            except Empty:
                continue

    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(consume_queue)
    return True


@socketio.on("disconnect", namespace="/websocket")
def io_disconnect():
    #emit("message", {"msg": "Goodbye World"}, namspace="/websocket")
    emit(
        "message", {"msg": "Goodbye World (from websocket server)"},
        namspace="/websocket")
    return True


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
#def build_dct_from(obj, names):
#  return dict( (name, getattr(obj, name)) for name in names )

#### @TODO: those two here have NOOO limits in size!!!! @FIXME
sig_queue = Queue()
sig_archive = {}


def default_signal_handler(sender, signal, *v, **kw):
    #print("DEFAULT HANDLER", signal, v, kw)
    global sig_queue, sig_archive
    x = {
        "stamp": time(),
        "sender": str(sender),
        "event_type": signal,
        "uuid": uuid4().int
    }
    while True:
        try:
            if "node" in kw:
                x["node_id"] = kw["node"].node_id
            if "value" in kw:
                x["value"] = kw["value"].data
                x["value_id"] = kw["value"].value_id
            sig_queue.put(x, timeout=5)
            sig_archive[x["uuid"]] = x
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
    #print(path)
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


###
### options
###


class Options(Resource):
    def get(self):
        return {"options": dict(zwave.raw_opts.items())}

    def patch(self):
        zwave.update_options(opt_parse.parse_args(strict=True))
        return {
            "options-state": "editable",
            "options": dict(zwave.raw_opts.items())
        }

    def post(self):
        zwave.update_options(opt_parse.parse_args(strict=True))
        ret = zwave.set_options()
        if "ok" in ret:
            return {
                "options-state": "locked",
                "options": dict(zwave.raw_opts.items())
            }
        else:
            abort(404)

    def delete(self):
        zwave.clear_options()
        return {
            "options-state": "empty",
            "options": dict(zwave.raw_opts.items())
        }


###
### "Table of contents"
###


@rest.get("/toc")
def list_routes():
    output = []
    for rule in app.url_map.iter_rules():
        options = {}
        for arg in rule.arguments:
            if arg in ["num", "node_id", "value_id"]:
                options[arg] = 123
            else:
                options[arg] = arg
        methods = ','.join(rule.methods)
        url = url_for(rule.endpoint, **options)
        line = urllib.parse.unquote("{:<35s} {:<40s} {:<20s}". \
                                    format(url, methods, rule.endpoint))
        output.append(line)
    return jsonify(list(sorted(output)))


###
### NETWORK
###
@rest.get("/net/signals")
def list_signals():
    from signals import net_signals
    return jsonify(net_signals)


@rest.get("/net/signals/latest/<int:num>")
def latest_signals(num):
    return jsonify(
        list(map(lambda x: (x[0], str(x[1]), x[2]), zwave.signals[-num:])))


@rest.get("/net")
def netinfo():
    if zwave.net is None:
        abort(414)
    return jsonify(zwave.net.to_dict())


@rest.post("/net/action/<string:member>")
def netaction(member):
    if (zwave.net is None
            and member != "start") and not hasattr(zwave.net, member):
        abort(404)

    ret = zwave.start() if member == "start" else \
        get_member(zwave.net, member, request.args)

    if zwave.net is None:
        abort(414)

    return jsonify({
        "returned": ret,
        "network-state": NetState(zwave.net.state).name,
        "executed-member": member,
        "network": zwave.net.to_dict()
    })


@rest.get("/net/actions")
def available_net_actions():
    if (zwave.net is None
            and member != "start") and not hasattr(zwave.net, member):
        abort(404)

    if zwave.net is None:
        abort(414)

    return jsonify([
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

    return jsonify([
        "start", "stop", "add_node", "assign_return_route", "cancel_command",
        "capabilities", "device", "is_primary_controller",
        "library_config_path", "library_description", "library_type_name",
        "library_user_path", "library_version", "name", "node", "node_id",
        "options", "owz_library_version", "python_library_config_version",
        "stats"
    ])


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
    return jsonify({
        "returned": ret,
        "ctrl-name": ctrl.name,
        "executed-action": member,
        "controller": ctrl.to_dict()
    })


@rest.get("/nodes")
def nodelist():
    if not zwave.net:
        abort(414)
    return jsonify(
        [{ "node_id": nid, "name": node.name, "location": node.location, "type": node.type, "specific": node.specific, \
           "product_name": node.product_name, "product_type": node.product_type, "product_id": node.product_id, \
            "manufacturer_name": node.manufacturer_name, "manufacturer_id": node.manufacturer_id } \
         for nid, node in zwave.net.nodes.items() ])


@rest.get("/node/<int:node_id>/values")
def node_values(node_id):
    return jsonify(zwave[node_id].values_to_dict())


class Node(Resource):
    def get(self, node_id):
        return dict(zwave[node_id].to_dict())

    def patch(self, node_id):
        node = zwave[node_id]
        for key, val in request.args.items():
            if key in [
                    "name", "location", "product_name", "manufacturer_name"
            ]:
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


api.add_resource(Options, "/net/opts")
api.add_resource(Node, "/node/<int:node_id>")
api.add_resource(NodeConfig, "/node/<int:node_id>/config")
api.add_resource(NodeValue, "/node/<int:node_id>/value/<int:value_id>")

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

