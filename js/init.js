"use strict";

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

/*function get_ctrl_action(action, args) {
    var ret;
    generic_ajax("POST", "/net/ctrl/action/" + action, {}, function(res) {
        ret = (res.error) ? res.error : res.returned;
    });
    return ret;
};*/

function camelcase2title(s) {
	return s.replace(/([A-Z])/g, " $1").replace(/^./, (str) => str.toUpperCase());
}

var IO = Object({
	log: function(text, stamp, event_type) {
		if (typeof stamp === "undefined" || stamp == null)
			stamp = Date.now();

		var d = new Date(stamp);
		if (typeof event_type === "undefined" || event_type == null)
			event_type = "Info Message";
		else
			event_type = camelcase2title(event_type);

		return $("#event_grid").jsGrid("insertItem", {
			stamp: stamp,
			Date: d.strftime("%d.%m.%Y"),
			Time: d.strftime("%H:%M:%S::") + stamp.toString().slice(-3),
			EventType: "<b>" + event_type + "</b>",
			Content: text
		}).then(function() {
			$("#event_grid").jsGrid("sort", {field: "stamp", order: "desc"});
		});
	}
});

class AjaxManager {
  constructor (base_url, gob)  {
		this.base_url = base_url;
		this.gob = gob;
	}

	generic_ajax(type, url, data, success_func) {
		var base_msg = type + "' request to: '" + url + "' with data: " + DumpObject(data);
		IO.log("ajax: " + base_msg);
		return $.ajax({
			type: type,
			url: url,
			data: data,
			error: function() {
				IO.log("Failed: '" + base_msg);
			},
			success: success_func
		});
	}

  node_foreach(cb_func) {
		return this.generic_ajax("GET", "/nodes", {}, function(res) {
			IO.log("Retrieving all nodes from server...");
			$("#node_grid").jsGrid("option", "data", []);
			return res.map(cb_func);
		});
	};



	net_opts(opts) {
			return this.generic_ajax("POST", "/net/opts", opts, function() {
        if (!$("#device_path").prop("disabled"))
            IO.log("Success adding option(s): " + DumpObject(opts));
 			});
	}

	net_action(act) {
		var inp = $("#device_path");
		return this.generic_ajax("POST", "/net/action/" + act, {}, function() {
			IO.log(act[0].toUpperCase() + act.slice(1).toLowerCase() + "ed controller & network");
		});
	}
}


function add_node(node) {
	  gob.num_nodes += 1;
    return $("#node_grid").jsGrid("insertItem", {
        "node_id": node.node_id,
        "name": node.name,
        "location": node.location,
        "type": node.type,
        "specific": node.specific,
        "product_name": node.product_name,
        "product_type": node.product_type,
        "product_id": node.product_id,
        "manufacturer_name": node.manufacturer_name,
        "manufacturer_id": node.manufacturer_id
    });
};


var config = {
	device_path: "/dev/ttyACM0",
	config_path: "/etc/openzwave",
	log_path: "OZWLog.log",
  user_path: "."
};


// gob == Global State Object
var gob = {
    // controller initilized?
    inited: false,
    // number of nodes
    num_nodes: 0,
    // maybe a container for often needed (dom)-elements?
    elems: {},
    // keep device path
	device_path: null
};

$( function() {

	class _inps {
		get device_path() { return $("#device_path"); }
		get user_path()   { return $("#user_path"); }
		get config_path() { return $("#config_path"); }
		get log_path()    { return $("#log_path"); }

		map(func) {
			return [this.device_path, this.user_path, this.config_path, this.log_path].map(elem => func(elem));
		}

	};
	var inps = new _inps();

 	var but_on = $("#device_on");
 	var but_off = $("#device_off");
 	var evts = $("#event_grid");

	const manager = new AjaxManager("", gob);

 /*	inp.click(function(ev) {
		if (inp.val().slice(0, 1) == "[")
			inp.val()
	});*/

    but_on.click(function() {
      var opts = new Object({
				device:      inps.device_path.val(),
				user_path:   inps.user_path.val(),
				config_path: inps.config_path.val(),
				log_file:    inps.log_path.val()
			});
      $.when( manager.net_opts(opts).done( () => manager.net_action("start") ) );
    });

    but_off.click(function() {
      manager.net_action("stop");
    });

	inps.map(elem => elem.val(config[elem.attr("id")]));

	// global event handler, if network goes (or is) running
	$( document ).on("ZWave::NetworkStarted", function() {
		manager.generic_ajax("POST", "/net/ctrl/action/device", {},
			(res) => {
				gob.device_path = res.returned;
				gob.inited = true;
				inps.map(elem => elem.prop("disabled", true));
				but_on.prop("disabled", true);
				but_off.prop("disabled", false);
				manager.node_foreach(add_node);
			});

	});
	// global event handler, if network goes (or is) down
	$( document ).on("ZWave::NetworkStopped", function() {
		gob.device_path = null;
		gob.inited = false;
		inps.map(elem => elem.prop("disabled", false));
		but_on.prop("disabled", false);
		but_off.prop("disabled", true);
	});


	// init and connect to websocket-based events
    var socket = io.connect("http://127.0.0.1:5000/websocket", {"transports": ["websocket"]});

    socket.on('connect',    function()     { IO.log("Websocket connected successfully");   });
    socket.on('disconnect', function()     { IO.log("Websocket disconnected successfuly"); });
    socket.on("message",    function(data) {
		console.log(data);
		// a stamp identifies as a ZWave originating "message"
        if (data.stamp) {
		  // trigger ZWave signal as custom JavaScript event!
          $( document ).trigger( "ZWave::" + data.event_type );
          // construct and insert event-log entry
		  var txt = (data.sender == "_Anonymous") ? "" : ("<b>From:</b> " + data.sender);
          if (data.node_id)
            txt += " <b>NodeID:</b> " + data.node_id;
          if (data.value || data.value_id)
            txt += " <b>Value:</b> " + data.value + " <b>ValueID:</b> " + data.value_id;
  		  IO.log(txt, data.stamp * 1000, data.event_type);
        } else
		  // websocket "message" not originating from ZWave
          IO.log(data.msg);
  });

  // jquery-ui init(s)
  $( ".top_box" ).controlgroup();
  $( ".top_box" ).controlgroup({"direction": "vertical"});

  // finally check if the network is up or down:
  manager.generic_ajax("GET", "/net", {}, function(res) {
    if (typeof res.error !== "undefined" || (typeof res.state !== "undefined" && res.state[0] == 0))
	  $( document ).trigger("ZWave::NetworkStopped");
    else
	  $( document ).trigger("ZWave::NetworkStarted");
  });


});
