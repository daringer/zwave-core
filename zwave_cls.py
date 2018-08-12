from flask_restful import reqparse

from openzwave.network import ZWaveNetwork
from openzwave.option import ZWaveOption

from pydispatch import dispatcher

from signals import net_signals

class ZWave:
    def __init__(self, error_handler):
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
                dispatcher.connect(self.default_signal_handler, sig)

    def default_signal_handler(sender, signal):
        print ("Caught SIGNAL....")
        print (sender)
        print (signal)
  
    def get_node(self, node_id, silentfail=False):
        if not self.net:
            self.err_handler(414)
        return self.net.nodes.get(node_id) or self.err_handler(404)

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


