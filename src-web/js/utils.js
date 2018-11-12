"use strict";

String.prototype.lpad = function(padString, length) {
    var str = this;
    while (str.length < length)
        str = padString + str;
    return str;
}

function DumpObject(obj, descent=false) {
    var od = new Object;
    var result = "";
    var len = 0;

    for (var property in obj) {
        var value = obj[property];
        if (typeof value == 'string') {
            value = "'" + value + "'";
        } else if (typeof value == 'object') {
            if (value instanceof Array) {
                value = "[ " + value + " ]";
            } else {
        	    value = "{...}";
                if (descent) {
        	        var ood = DumpObject(value);
                    value = "{ " + ood.dump + " }";
                }
            }
        }
        result += "'" + property + "' : " + value + ", ";
        len++;
    }
    od.dump = result.replace(/, $/, "");
    od.len = len;
    return result.slice(0, -2);
};

function camelcase2title(s) {
	return s.replace(/([A-Z])/g, " $1").replace(/^./, (str) => str.toUpperCase());
}

var log_types = Object({
		log:  [ 5, "Log Message"],
		dbg:  [10, "Debug Message"],
		info: [ 7, "Info Message"],
		err:  [ 3, "Error Message"],
		ret:  [ 4, "Return Message"]
	});

var IO = Object({

	log: function(text, stamp, event_type) {
		if (typeof stamp === "undefined" || stamp == null)
			stamp = Date.now();

		var d = new Date(stamp);
		if (typeof event_type === "undefined" || event_type == null)
			event_type = log_types["info"][1];
		else if(event_type in log_types)
			event_type = log_types[event_type][1];
		else
			event_type = camelcase2title(event_type);

		return $("#event_grid").jsGrid("insertItem", {
			stamp: stamp,
			Date: d.strftime("%d.%m.%Y"),
			Time: d.strftime("%H:%M:%S::") + stamp.toString().slice(-3),
			EventType: "<b>" + event_type + "</b>",
			Content: text
		}).then(function() {
			//$("#event_grid").jsGrid("sort", {field: "stamp", order: "desc"});
		});
	},

	err: function(text, stamp) {
		this.log(text, null, "err");
	},

	warn: function(text, stamp) {
		this.log(text, null, "warn");
	},

	debug: function(data) {
		var _mydata = [];
		if (typeof data === "object") {
			var keys = Object.keys(data);
			if (keys.length == 1 && keys[0] == "msg") {
				this.log(data.msg);
				return;
			}
			for (var key of keys) {
			  if (key == "value") {

				  if (data.value != null && data.value == 255)
					_mydata.push(`data.value: ${data.value}`)

				  else if (data.value != null && "value_id" in data.value)
	  				_mydata.push(`value_id: ${data.value.value_id}`);

				  else if(data.value != null && "data" in data.value)
  					_mydata.push(`value_data: ${data.value.data}`);

			  } else if (key == "node" && data.node != null) {

					if (data.node != "ZWaveController" && "node_id" in data.node)
					  _mydata.push(`node_id: ${data.node.node_id}`);
					else
						_mydata.push("node: ZWaveController");



			  } else if (key != "event_type" && key != "args") {
					if (data[key] == null)
						_mydata.push(`${key}=null}`);
					else
						_mydata.push(`${key}=${data[key].toString()}`);
				}
			}
			if ("args" in data && typeof args == "object") {
				for (var arg_key of Object.keys(data.args)) {
					if (data.args[arg_key] != null)
					  _mydata.push(`arg:${arg_key}=${data.args[arg_key].toString()}`);
				}
			}
		}
		this.log(_mydata.join(", "), Date.now(), data.event_type);
	}

});



