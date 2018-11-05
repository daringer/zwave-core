"""
For consistency all json responses shall be assembled here.
The json msg will then always be structured like this,
all components are optional:
  dict({
    error:   <numeric>          if present, indicates an error
    msg:     <message>          human-readable user designated message
    data:    <any data>         arbitrary data (payload), the user has to ensure
                                that its contents are json-friendly
    states:  <dict of states>   contains all state(s) encountered during the last request
                                (not implemented yet)
"""

from flask import jsonify

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

"""
The following functions provide shortcuts for the Ajax response factory class:
- jsonify()-ed output (if flask-restful isn't used i.e., no Resource),
  each function provides a `ret_j*` variant for json-output and a regular version
- each one may take `msg` to provide a message to the user, independent of the
  actually delivered content
- `ret_ajax()` is meant to provide any json-able `data`
- `ret_err()` reports an error using `code` (numeric) and a `msg`
- `ret_msg()` delivers any `msg`
"""
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


