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

	log: function(text, stamp, event_type, event_uuid) {
		if (typeof stamp === "undefined" || stamp == null)
			stamp = Date.now();

		if (typeof event_uuid == "undefined" || event_uuid == null)
			event_uuid = "n/a";

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
			Event: "<b alt=" + event_uuid + " >" + event_type + "</b>",
			Content: text
		})
	},

	err: function(text, stamp) {
		this.log(text, null, "err", "n/a");
	},

	warn: function(text, stamp) {
		this.log(text, null, "warn", "n/a");
	},

	debug: function(data) {
		this.log(data.join(", "), data.stamp,  data.signal, data.uuid);
	}

});



