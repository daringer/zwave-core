from flask_restful import reqparse
from openzwave.network import ZWaveNetwork
from openzwave.object import ZWaveException
from openzwave.option import ZWaveOption
from pydispatch import dispatcher

from signals import net_signals

# import openzwave
from openzwave.node import ZWaveNode
from openzwave.value import ZWaveValue
# from openzwave.scene import ZWaveScene
# from openzwave.controller import ZWaveController
# from openzwave.network import ZWaveNetwork

class ZWaveCentralException(ZWaveException):
    pass

class ZWave:
    def __init__(self, error_handler, sig_handler):
        self.ctrl = []
        self.net = None
        self.home_id = None
        self.uid2node_val = {}

        self.raw_opts = reqparse.Namespace()
        self.opts = None
        self.opts_locked = False

        self.err_handler = error_handler

        for sig, handler in net_signals:
            if handler is None:
                dispatcher.connect(
                    sig_handler, signal=sig, sender=dispatcher.Any)

    def get_node(self, node_id, silentfail=False):
        if not self.net:
            self.err_handler(414)
        out = self.net.nodes.get(node_id)
        return out

    def get_main_ctrl(self):
        return None if len(self.ctrl) == 0 else self.ctrl[0]

    def __contains__(self, node_id):
        return node_id in self.net.nodes

    def __getitem__(self, node_id):
        return self.get_node(node_id)

    def get_node_details(self, node_id, fields=None, silentfail=False):
        if not self.net:
            self.err_handler(414)

        node = self.get_node(node_id)
        fields = fields or ["node_id", "name", "query_stage"]

        return dict((f, getattr(node, f)) for f in fields if hasattr(node, f))

    def update_options(self, opts):
        self.raw_opts.update(opts)

    def clear_options(self):
        self.opts_locked = False
        self.opts = None
        self.raw_apts = reqparse.Namespace()

    def set_options(self):
        opts = self.raw_opts
        self.opts = ZWaveOption(
            device=opts.get("device"),
            config_path=opts.get("config_path"),
            user_path=opts.get("user_path"),
            cmd_line=opts.get("cmd_line"))
        for key, val in opts.items():
            if key not in ["device", "config_path", "user_path", "cmd_line"]:
                getattr(self.opts, "set_" + key)(val)
        self.opts.lock()
        self.opts_locked = True

    def start(self):
        if not self.opts_locked:
            raise ZWaveCentralException("ZWave options not locked")
        self.net = ZWaveNetwork(self.opts, autostart=False)
        self.ctrl.append(self.net.controller)

        self.home_id = self.net.home_id
        self.net.start()

    def get_groups(self, node_id):
        my_groups = {}
        for idx, grp in self.get_node(node_id).groups.items():
            my_groups[idx] = grp.to_dict()
            my_groups[idx]["index"] = idx
            my_groups[idx]["max_associations"] = grp.max_associations
            my_groups[idx]["cur_associations"] = len(grp.associations)
            my_groups[idx]["max_count"] = grp.max_associations
            my_groups[idx]["cur_count"] = len(grp.associations)

        return my_groups

def get_member(src, attr_name, args, env):
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

