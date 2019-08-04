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

from consts import GROUP_MEMBERS, GROUP_ATTRS, GROUP_EXTRA_ATTRS, \
        VALUE_MEMBERS, VALUE_ATTRS, VALUE_EXTRA_ATTRS, \
        NODE_MEMBERS, NODE_ATTRS, NODE_EXTRA_ATTRS


class ZWaveCentralException(ZWaveException):
    pass


class ZWaveCoreBaseClass:
    def __init__(self, ozw_obj, wrapped_members=None, show_attrs=None, extra_attrs=None):
        """
        - `ozw_obj` holds the original python-openzwave instance of this zwave-item
        - `wrapped_members` is a list of members within `ozw_obj` to be passed through i.e., wrapped
        - `extra_attrs` constains a list of attrs extending the object, but these are obviously to
          be found within the wrapping object instance
        - `show_attrs` contains a list of attrs to be shown, if the object is being asked to provide
          its ::to_dict() output
        """
        # init openzwave object as member
        object.__setattr__(self, "_ozw_obj", ozw_obj)
        object.__setattr__(self, "_wrapped_members", (set(wrapped_members) - set(extra_attrs)) or [])
        object.__setattr__(self, "_extra_attrs", extra_attrs or [])
        object.__setattr__(self, "_show_attrs", show_attrs or [])

    def __getattr__(self, key):
        if key in self._wrapped_members:
            try:
                return getattr(self._ozw_obj, key)
            except TypeError as e:
                print ("TypeError - key: {key}")
                print(e)
                return None
        return object.__getattribute__(self, key)

    def __setattr__(self, key, val):
        obj = self._ozw_obj if key in self._wrapped_members else self
        return object.__setattr__(obj, key, val)

    def __hasattr__(self, key):
        return key in self._wrapped_members + self.__dict__.keys()

    def to_dict(self, excludes=None):
        out = {}
        excludes = excludes or []
        for attr in self._show_attrs:
            if attr not in excludes and hasattr(self, attr):
                out[attr] = getattr(self, attr)
        return out

class ZWaveCoreGroup(ZWaveCoreBaseClass):
    def __init__(self, ozw_obj):
        super().__init__(ozw_obj, GROUP_MEMBERS, GROUP_ATTRS, GROUP_EXTRA_ATTRS)
        self.cur_associations = len(self.associations)
        self.max_count = self.max_associations
        self.cur_count = len(self.associations)

    def to_dict(self):
        out = super().to_dict()
        for key, val in out.items():
            if isinstance(val, set):
                out[key] = list(val)
        return out


class ZWaveCoreValue(ZWaveCoreBaseClass):
    def __init__(self, ozw_obj):
        super().__init__(ozw_obj, VALUE_MEMBERS, VALUE_ATTRS, VALUE_EXTRA_ATTRS)

class ZWaveCoreNode(ZWaveCoreBaseClass):
    def __init__(self, ozw_obj):
        super().__init__(ozw_obj, NODE_MEMBERS, NODE_ATTRS, NODE_EXTRA_ATTRS)
        self._values = None
        self._groups = None

    @property
    def values(self):
        if not self._values:
            self._values = {}
            for val_obj in self._ozw_obj.values.values():
                self._values[val_obj.value_id] = ZWaveCoreValue(val_obj)
        return self._values

    @property
    def groups(self):
        if not self._groups:
            self._groups = {}
            for idx, grp in self._ozw_obj.groups.items():
                self._groups[idx] = ZWaveCoreGroup(grp)
        return self._groups

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

        #self.node_cache = {}

        for sig, handler in net_signals:
            if handler is None:
                dispatcher.connect(
                    sig_handler, signal=sig, sender=dispatcher.Any)

    def get_node(self, node_id, silentfail=False):
        if not self.net:
            self.err_handler(414)

        #out = None
        #if not node_id in self.node_cache:
        #    out = ZWaveCoreNode(self.net.nodes.get(node_id))
        #self.node_cache[node_id] = out

        #if out is None:
        #    raise Exception("shit")

        #print (f"soifjoidsojidf: {node_id}")
        inner = self.net.nodes.get(node_id)
        out = ZWaveCoreNode(inner)
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

