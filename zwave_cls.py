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

    #@property
    #def nodes(self):
    #    return self.net.nodes

    def get_node(self, node_id, silentfail=False):
        #if isinstance(node_id, ZWaveNode):
        #    return node_id
        if not self.net:
            self.err_handler(414)

        #self.nodes = self.net.nodes
        #if len(self.nodes) != len(self.net.nodes):
        #    for n_id, node in self.net.nodes.items():
        #        #node.__class__ = Node
        #        #self.nodes[n_id] = node
        #        #for val_id, val in node.values.items():
        #        #    val.__class__ = NodeValue
        #
        #    self.nodes = dict((node_id, Node(node_id, self.net))
        #        for node_id, node in self.net.nodes.items())
        #print (self.net.nodes.get(node_id).values)
        #print (self.nodes.get(node_id).values)
        out = self.net.nodes.get(node_id)
        #ret = Node(self.net.nodes.get(node_id), self.net)
        #dct = {}
        #for val in out.values.values():
        #    self.uid2node_val[val.uid] = (node_id, val)
            #dct[val.uid] = val
        #out.values = dct
        return out

    def __getitem__(self, node_id):
        return self.get_node(node_id)

    def get_node_details(self, node_id, fields=None, silentfail=False):
        if not self.net:
            self.err_handler(414)

        node = self.get_node(node_id)
        fields = fields or ["node_id", "name", "query_stage"]

        return dict((f, getattr(node, f)) for f in fields if hasattr(node, f))

    #def get_value_by_uid(self, uid):
    #    return self.uid2node_val.get(uid, (None, None))

    #def set_value_by_uid(self, uid, val):
    #    node_id, tar_val = self.uid2node_val[uid]
    #    set_val = tar_val.check_data(val)
    #    if set_val is not None:
    #        #tar_val.data = set_val
    #        self[node_id].values[tar_val.value_id].data = set_val
    #    else:
    #        raise ZWaveCentralException("provided value is bad: {}".format(val))
    #    return True

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

