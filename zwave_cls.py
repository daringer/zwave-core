from flask_restful import reqparse

from openzwave.network import ZWaveNetwork
from openzwave.option import ZWaveOption

# import openzwave
# from openzwave.node import ZWaveNode
# from openzwave.node import ZWaveNode
# from openzwave.value import ZWaveValue
# from openzwave.scene import ZWaveScene
# from openzwave.controller import ZWaveController
# from openzwave.network import ZWaveNetwork
# from openzwave.option import ZWaveOption

from pydispatch import dispatcher

from signals import net_signals


class Node:
    def __init__(self, zwave_node):
        self.raw_node = zwave_node

    @property
    def values(self):
        return self.raw_node.get_values()

    def get_configs(self):
        self.raw_node.request_all_config_params()

    @property
    def configs(self):
        return self.raw_node.config

    def __getattr__(self, key):
        return getattr(self.raw_node, key)


class ZWave:
    def __init__(self, error_handler, sig_handler):
        self.ctrl = []
        self.net = None
        self.nodes = None
        self.home_id = None

        self.raw_opts = reqparse.Namespace()
        self.opts = None
        self.opts_locked = False

        self.err_handler = error_handler

        for sig, handler in net_signals:
            if handler is None:
                dispatcher.connect(sig_handler, signal=sig, sender=dispatcher.Any)
                #print("connecting sig_handler: {}".format(sig_handler))

    def get_node(self, node_id, silentfail=False):
        if not self.net:
            self.err_handler(414)
        return Node(self.net.nodes.get(node_id)) or self.err_handler(404)

    def __getitem__(self, node_id):
        return self.get_node(node_id)

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
            cmd_line=opts.get("cmd_line")
        )
        for key, val in opts.items():
            if key not in ["device", "config_path", "user_path", "cmd_line"]:
                getattr(self.opts, "set_" + key)(val)
        self.opts.lock()
        self.opts_locked = True

    def start(self):
        if not self.opts_locked:
            return {"fail": "options not locked"}
        self.net = ZWaveNetwork(self.opts, autostart=False)
        self.ctrl.append(self.net.controller)
        self.nodes = self.net.nodes
        self.home_id = self.net.home_id
        self.net.start()

