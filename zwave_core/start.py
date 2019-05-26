import functools
import os
import urllib
from enum import IntEnum
from time import time, sleep
from uuid import uuid4
import json
import sys
import yaml
from hashlib import md5

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
from openzwave.network import ZWaveNetwork
from openzwave.controller import ZWaveController
from openzwave.option import ZWaveOption

from enums import NetState, OptionState, FrontendAction


###### own
from parsers import nodes_parse, opt_parse, value_parse, group_parse, node_field_parse
from zwave_cls import ZWave, get_member
from ajax_builder import Ajax, ret_ajax, ret_jajax, ret_err, \
        ret_jerr, ret_msg, ret_jmsg
# @TODO: get rid of to_json(), worst possible implementation :(
from utils import listify, to_json, ItemsToAttrs

from consts import *

from mqtt_client import MyMQTTClient

### load config
cfg_fn = "zwave_core.yaml"
if len(sys.argv) >= 3:
    assert sys.argv[1] == "-c"
    cfg_fn = sys.argv[2]
if not os.path.exists(cfg_fn):
    print (f"Cannot start without config file: {cfg_fn}")

cfg = ItemsToAttrs({})
with open(cfg_fn, "rb") as fd:
    cfg = ItemsToAttrs(yaml.load(fd))



signals_debug = cfg.debug.signals

app = Flask(__name__)
app.config['SECRET_KEY'] = cfg.secret

api = Api(app)

@api.representation('application/json')
def output_json(data, code, headers=None):
    """overwrite application/json based responses"""
    data = to_json(data)
    resp = make_response(json.dumps(data), code)
    resp.headers.extend(headers or {})
    return resp


# bring up our async tooling
socketio = SocketIO(app, async_mode="eventlet")
thread = None
thread_lock = Lock()

# do not touch for now, but undeniably needs improvements: @TODO
@socketio.on("connect", namespace="/websocket")
def io_connect():
    emit("message", {"msg": "Hello World (from websocket server)"},
         namespace="/websocket")

    def consume_queue():
        """queue worker / consumer"""
        global sig_queue
        while True:
            try:
                item = sig_queue.get(timeout=5)
                socketio.send(to_json(item), namespace="/websocket")
                #socketio.send(json.dumps(item), namespace="/websocket")

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


# "Error handling"
# @TODO: find some neat scheme to have consistent error-handlers
#        (i.e., stop abusing http-errorcodes here!)
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


# @TODO: all (web-)socket related components shall be in one place...
sig_queue = Queue()
#sig_archive = {}


class SignalManager(object):
    none_repl = "n/a"

    def __init__(self):
        pass

    def parse_signal(self, when, sender, sig, uuid, more_args, more_kw):
        if signals_debug:
            print ("\n\n")
            print ("---- SignalManager ----")
            print ("when:", when, "sender:", sender, "sig:", sig, "uuid:", uuid)
            print ("args:", more_args, more_kw)

        out = self.trim(more_kw)
        out["sender"] = sender
        out["signal"] = sig
        out["uuid"] = uuid
        out["stamp"] = when

        if str(sender) == "_Anonymous":
            del out["sender"]

        #if sig == "ValueChanged":
        #    out["frontend_action"] = FrontendAction.update_value
        #elif sig == "ValueAdded":
        #    out["frontend_action"] = FrontendAction.add_value | FrontendAction.update_value

        if signals_debug:
            print("PARSED:", out)

        return out


    def trim(self, more_kw):
        out = {}
        my_iter = more_kw.items() if isinstance(more_kw, dict) else enumerate(more_kw)
        for key, value in my_iter:
            if value is None or value == 'None' or value == 'None.':
                out[key] = self.none_repl
                continue

            if key == "network":
                pass
            elif key == "controller":
                try:
                    out["ctrl_node_id"]  = str(value.node_id)
                except Exception as e:
                    out["ctrl_node_id"] = "<get failed>"
                    out["ctrl_node_id_error"] = str(e)
            elif key == "node":
                out["node_id"] = value.node_id
            elif key == "node_id" and value == 0:
                out[key] = self.none_repl
            elif key == "value":
                out["value_id"] = value.value_id
                out["value_data"] = value.data
            else:
                out[key] = str(value)
        return out

sig_manager = SignalManager()


# this by far does not look trustworthy,
# @TODO: realize a less fear-driven solution
# @TODO: also need serious pre-parsing and handling of events on server side!
# @TODO: means we have to understand every single signal and send only a condensed
#        version to the frontend, there no parsing should happen, just visualization!
def default_signal_handler(sender, signal, *v, **kw):
    """Signal header for the 'louie' Z-Wave emitted signals"""
    global sig_queue, sig_manager #, sig_archive
    if signals_debug:
        print ("DEFAULT HANDLER:", signal)

    to_send = sig_manager.parse_signal(time(), sender, signal, uuid4().int % ((2**32)-1), v, kw)

    while True:
        try:
            if signals_debug:
                print ("ENQUEING:", type(to_send), to_send)
            sig_queue.put(to_send, timeout=5)
            #sig_archive[x["uuid"]] = x
            break
        except Full:
            if signals_debug:
                print ("ENQUE failed, retrying...")
            # queue full, wait a little
            sleep(1.0)
            continue
    return True




def action_handler(attrs, sub_act_dct, wrap_dct, action, args, src, zwave_obj):
    """
    Generic `action_handler` for python-openzwave `action`s exposed via the REST-API.
    - if `action` inside "show" group: run `get_member()` on `action`, `args` and `zwave_obj`
    - otherwise `action` might be "wrapped" leading to call of wrapped function: wrap()
    - or `action` "converts" action, args + zwave_obj to be used with original action
    """
    if signals_debug:
        print(f"action_handler with action: {action} and args: {args}")
    # found in regular action list
    if action in sub_act_dct["show"]:
        if signals_debug:
            print (f"EXECUTING: {action} using args: {args}")
        return get_member(src, action, args, zwave_obj)

    wrap = wrap_dct.get(action)
    if wrap is not None:
        if callable(wrap):
            if signals_debug:
                _node_id = "<none>" if (src is None or not hasattr(src, "node_id")) else src.node_id
                print (f"WRAPPING: {action} using args: {args} as callable node_id: {_node_id}")
            # either a callable() replacing the original call
            return wrap(src, action, args, zwave_obj)
        else:
            # or simply a (action, my_args) => (new_action, my_new_args) converter
            if signals_debug:
                print (f"WRAPPING: {action} using args: {args} as converter")
            new_action, new_args = wrap(src, action, args, zwave_obj)
            return get_member(src, new_action, new_args, zwave_obj)

    # RAISE exception here
    print (f"ACTION HANDLER: failed act: {action} args: {args}")
    return None


###
### (web)page(s)
###
if cfg.frontend.active:
    PATH_TO_WEB = "src-web"
    @app.route("/static/<string:path>")
    @app.route("/static/js/<string:path>")
    def frontend_static(path):
        js_path = os.path.join(PATH_TO_WEB, "js", path)
        path = os.path.join(PATH_TO_WEB, path)
        if not os.path.exists(path):
            if not os.path.exists(js_path):
                abort(404)
            else:
                path = js_path

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
        path = os.path.join(PATH_TO_WEB, "frontend.html")
        with open(path) as fd:
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
        try:
          msg = "Could not open zwave serial device: {} [permissions?]".format(p)
          if p is None or not os.path.exists(p) or \
              (not open(p, "rb").readable()) or \
              (not open(p, "wb").writable()):
                  print ("bad device path: {}".format(p))
                  return ret_err(404, msg)
        except PermissionError as e:
          return ret_err(404, msg + " Exception: " + str(e))

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

## "Table of contents" REST-style
@rest.get("/toc")
def list_routes():
    from random import randint
    output = []
    for rule in app.url_map.iter_rules():
        options = {}
        opt2str = {}
        for arg in rule.arguments:
            if arg in ["num", "node_id", "value_id", "index"]:
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

##
## Z-Wave network views
##
@rest.get("/net/signals")
def list_signals():
    from signals import net_signals
    return ret_jajax([sig[0] for sig in net_signals])

@rest.get("/net")
def netinfo():
    if zwave.net is None:
        return ret_jerr(404, "Network and/or Controller inactive")
    return ret_jajax(zwave.net.to_dict())

@rest.post("/net/action/<string:action>")
def netaction(action):
    """exec an 'action', restricted to the listed ones (for now)"""
    if action not in (NET_ACTIONS + NET_ATTRS):
        return ret_jerr(404, "Requested action: {} not available".format(action))
    if (zwave.net is None and action != "start") and not action in NET_ACTIONS:
        return ret_jerr(404, "Network and/or Controller inactive")

    ret = action_handler(NET_ATTRS, NET_SUB_ACTIONS, NET_WRAPPED, action, request.args,
                         zwave.net, zwave)

    if zwave.net is None:
        return ret_jerr(404, "Network and/or Controller inactive")

    return Ajax(data={"returned": ret, "executed": action}, jsonify=True) \
        .set_state("net", NetState(zwave.net.state)).render()

@rest.get("/net/actions")
def available_net_actions():
    if zwave.net is None:
        return ret_jerr(404, "Network and/or Controller inactive")
    return ret_jajax((NET_ACTIONS + NET_ATTRS))

##
## Z-Wave controller views
##
@rest.post("/net/ctrl/action/<string:action>")
def ctrlaction(action, ctrl_idx=0):
    ctrl = zwave.ctrl[ctrl_idx] if len(zwave.ctrl) > ctrl_idx else None
    if ctrl is None or not zwave.net:
        return ret_jerr(404, "Network and/or Controller inactive")
    if action not in (CTRL_ACTIONS + CTRL_ATTRS):
        return ret_jerr(404, "Requested action: {} not available".format(action))

    ret = action_handler(CTRL_ATTRS, CTRL_SUB_ACTIONS, CTRL_WRAPPED, action, request.args,
                         zwave.get_main_ctrl(), zwave)

    if isinstance(ret, set):
        ret = list(sorted(ret))

    return ret_jajax({
        "returned": ret,
        "executed": action,
        "controller": ctrl.to_dict()
    })


# @TODO: same as for network here w.r.t. arg passing
@rest.get("/net/ctrl/actions")
def available_ctrl_actions(ctrl_idx=0):
    ctrl = zwave.ctrl[ctrl_idx] if len(zwave.ctrl) > ctrl_idx else None
    if ctrl is None or not zwave.net:
        return ret_jerr(404, "Network and/or Controller inactive")

    # @TODO: order these similar to the ones in node (also seperate POST/GET)
    return ret_jajax((CTRL_ACTIONS + CTRL_ATTRS))

@rest.get("/nodes")
def nodelist():
    if not zwave.net:
        return ret_jerr(404, "Network and/or Controller inactive")

    return ret_jajax([to_json(zwave.get_node_details(node_id, NODE_ATTRS)) \
                      for node_id in zwave.net.nodes])

class Node(Resource):
    def get(self, node_id):
        """
        @TODO: avoid sending ALL information here, only minimal data like ?????
               other data shall then be acquired via calls to node/<node_id>/[groups,values,stats,...]
        """
        node = zwave.get_node(node_id)
        is_ctrl = node.role == "Central Controller" and "primaryController" in node.capabilities

        return ret_ajax({
            "values": dict((v.value_id, v.to_dict()) for v in node.values.values()),
            "actions": NODE_ACTIONS,
            "groups": dict((g.index, g.to_dict()) for g in node.groups.values()),
            "stats": node.stats,
            "is_ctrl": is_ctrl,
            "ctrl_stats": zwave.ctrl[0].stats if is_ctrl else ""
        })

    def patch(self, node_id):
        node = zwave[node_id]
        data = node_field_parse.parse_args(strict=True)
        node.set_field(data.field_name, data.field_value)
        return ret_msg(msg="field: {} successfully set to: {}". \
                       format(data.field_name, data.field_value))

@rest.get("/node/actions")
def node_actions():
    return ret_jajax((NODE_ACTIONS + NODE_ATTRS))

@rest.post("/node/<int:node_id>/action/<string:action>")
def node_action(node_id, action):
    if node_id not in zwave:
        return ret_jerr(404, "node-id: {} does not exist".format(node_id))

    if action not in (NODE_ACTIONS + NODE_ATTRS):
        return ret_jerr(404, "Requested action: {} not available".format(action))

    ret = action_handler(NODE_ATTRS, NODE_SUB_ACTIONS, NODE_WRAPPED, action, request.args,
                         zwave.get_node(node_id), zwave)

    return ret_jmsg(msg="Action: {} sent for node-id: {} returned: {}". \
                    format(action, node_id, str(ret)))


@rest.get("/node/<int:node_id>/groups")
def getgroups(node_id):
    x = [g.to_dict() for g in zwave.get_node(node_id).groups.values()]
    return ret_jajax(x)

class NodeGroup(Resource):
    def get(self, node_id, index):
        grp = zwave.get_node(node_id).groups.get(index).to_dict()
        if grp is not None:
            return ret_ajax(grp)
        return ret_err(404, f"group at index: {index} in node_id: {node_id}, not found")

    def put(self, node_id, index):
        grp = zwave.get_node(node_id).groups.get(index)
        if grp is None:
            return ret_err(404, f"group at index: {index} in node_id: {node_id}, not found")

        target_node_id = group_parse.parse_args(strict=True).target_node_id
        if target_node_id is None:
            print (f"no or bad data provided: {target_node_id}")
            abort(404)

        zwave.get_node(node_id).groups.get(index).add_association(target_node_id)
        #zwave[node_id].groups[index].add_association(target_node_id)
        return ret_msg(msg=f"added node_id: {target_node_id} to group: {index}")

    def delete(self, node_id, index):
        #grp = zwave[node_id].groups.get(index)
        grp = zwave.get_node(node_id).groups.get(index)
        if grp is None:
           return ret_err(404, f"group at index: {index} in node_id: {node_id}, not found")

        target_node_id = group_parse.parse_args(strict=True).target_node_id

        if target_node_id is None:
            print (f"no or bad data provided: {target_node_id}")
            abort(404)

        if target_node_id not in grp.associations:
            return ret_err(404, f"target_node_id: {target_node_id} not found in grp: {index}")

        #zwave[node_id].groups[index].remove_association(target_node_id)
        zwave.get_node(node_id).groups.get(index).remove_association(target_node_id)

        return ret_msg(msg=f"removed node_id: {target_node_id} from group: {index}")

#class NodeConfig(Resource):
#    def get(self, node_id):
#        return ret_ajax(dict(zwave[node_id].to_dict()))
#
#    def post(self, node_id):
#        return ret_ajax(dict(zwave[node_id].to_dict()))

class NodeValue(Resource):
    def get(self, node_id, value_id):
        return ret_ajax(zwave.get_node(node_id).values.get(value_id).to_dict())

    def post(self, node_id, value_id):
        print ("NODE VALUE SET:", node_id, " VALID: ", value_id)
        data = value_parse.parse_args(strict=True).data
        if data is None:
            print ("no or bad data provided: {}".format(data))
            abort(404)

        node_vals = zwave.get_node(node_id).values #[node_id].values
        if value_id not in node_vals:
            return ret_err(404, msg=f"ValueID not found: {value_id} node_id: {node_id}")

        data = node_vals[value_id].check_data(data)
        if data is None:
            print (f"data contents are crap: {data}, check_data() failed...")
            abort(405)
        node_vals[value_id].data = data

        return ret_msg(msg="data for value set successfully")

api.add_resource(Options,       "/net/opts")
api.add_resource(NodeGroup,     "/node/<int:node_id>/group/<int:index>")
#api.add_resource(NodeConfig,    "/node/<int:node_id>/config")
api.add_resource(NodeValue,     "/node/<int:node_id>/value/<int:value_id>")
api.add_resource(Node,          "/node/<int:node_id>")

zwave = ZWave(abort, default_signal_handler)


#try:
#    mqtt = MyMQTTClient(cfg.mqtt.manager.host, cfg.mqtt.manager.port)
#    mqtt.start()
#except Exception as e:
#    print(e)


@rest.get("/mqtt")
def run_mqtt():

    if not cfg.mqtt.active:
        return ret_jerr("MQTT not active")

    if cfg.mqtt.topics.raw:
        for node_id in zwave.net.nodes:
            node = zwave.get_node(node_id)
            topic = f"{cfg.mqtt.topics.raw}/node/{node.node_id}"
            mqtt.publish(topic, node.to_dict())


    if cfg.mqtt.topics.ha:
        for node_id in zwave.net.nodes:
            node = zwave.get_node(node_id)

            dev_dct = {
              "identifiers": [10000 + int(node_id)],
              "manufacturer": node.manufacturer_name,
              "model": node.product_name,
              "name": node.name or ("node_id " + str(node_id))
            }

            for value_id, value in node.values.items():
                comp = None
                cmd_cls = value.command_class
                if cmd_cls == 37:
                    comp = "switch"
                elif cmd_cls in [49, 50]:
                    comp = "sensor"
                else:
                    print (f"unhandled COMMAND CLS: {cmd_cls}")
                    continue

                _t = f"{cfg.mqtt.topics.ha}/{comp}/{node.node_id}/{value_id}/"

                # HA auto-discover stuff
                cfg_topic = _t + "config"
                myname = node.name or ("node_" + str(node.node_id))
                payload = {
                  "unique_id": md5(bytes(str(node.node_id) + "___" + str(value_id), "ascii")).hexdigest(),
                  "name": value.label,
                  "device": dev_dct
                }

                state_topic = _t + "state"
                command_topic = _t + "set"
                if comp == "switch":
                    payload["command_topic"] = command_topic
                elif comp in ["sensor", "switch"]:
                    payload["state_topic"] = state_topic
                mqtt.publish(cfg_topic, json.dumps(payload))

                if comp == "switch":
                    mqtt.subscribe(command_topic)

                # state publish (
                state_topic = _t + "state"
                mqtt.publish(state_topic, value.data)

    return ret_jmsg("MQTT topics populated")

if __name__ == '__main__':

    ####### regular
    #app.run(debug=True)

    ####### eventlet
    app.debug = cfg.debug.flask
    socketio.run(app, host=cfg.api.bind.host, port=cfg.api.bind.port, debug=cfg.debug.socketio)

    ####### aiohttp
    #socketio.attach(app)
    #app.run(debug=True)

    ####### eventlet Middleware
    #app = socketio.Middleware(sio)
    #eventlet.wsgi.server(eventlet.listen(('', 8000)), app)
