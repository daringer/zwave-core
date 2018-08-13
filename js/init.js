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

function get_nodes() {
    generic_ajax("GET", "/nodes", {}, function(res) {
        add_event(Date.now(), "Retrieving all nodes from server...");
        console.log(res);
        for (var item  in res) {
            //var value = obj[property];
            add_node(zwave[item.node_id]);
        }
    });
};

function add_event(stamp, text, event_type) {
    d = new Date(stamp);
    if (event_type == null)
        event_type = "Info Message";
	return $("#event_grid").jsGrid("insertItem", {
		stamp: stamp, 
        Date: d.strftime("%d.%m.%Y"),
		Time: d.strftime("%H:%M:%S::") + stamp.toString().slice(-3),
        EventType: "<b>" + event_type + "</b>",
		Content: text
	}).then(function() {
		$("#event_grid").jsGrid("sort", {field: "stamp", order: "desc"});
	});
};

function add_node(node) {
    return $("#node_grid").jsGrid("insertItem", {
        "NodeID": node.node_id,
        "Name": node.name,
        "Location": node.location, 
        "Product Name": node.product_name, 
        "Manufacturer Name": node.manufacturer_name
    });
};

function generic_ajax(type, url, data, success_func) {
	return $.ajax({ 
		type: type, 
		url: url, 
		data: data, 
		error: function() {
			add_event(Date.now(), ("Failed: '" + type + "' request to: '" +
				url + "' with data: " + DumpObject(data)));
		},
		success: success_func
	});
};

function post_opts(resp=null, status=null, xhr=null, opts) {
 	return generic_ajax("POST", "/net/opts", opts, function() {
        if (!$("#device_path").prop("disabled"))
            add_event(Date.now(), "Success adding option(s): " + DumpObject(opts));
 	}).done(post_net_start);
};

function post_net_start(resp=null, status=null, xhr=null) {
    var inp = $("#device_path");
    var act = (inp.prop("disabled")) ? "stop" : "start";
	return generic_ajax("POST", "/net/action/" + act, {}, function() {
 		add_event(Date.now(), act[0].toUpperCase() + act.slice(1).toLowerCase() + "ed controller & network");
 		set_init_button(inp.prop("disabled"));
 	});
};

function set_init_button(show_init) {
    var inp = $("#device_path");
    var but = $("#init_device");
    if(show_init) {
        inp.prop("disabled", false);
 	    but.html("init device");
    } else {
 	    inp.prop("disabled", true);
 	    but.html("close device");
    }
};


$( function() {
 	var inp = $("#device_path");
 	var but = $("#init_device");
 	var evts = $("#event_grid");
 	inp.val("/dev/ttyACM0");

    //var socket = io.connect("http://" + document.domain + ":" + location.port + "/websocket"); //, {"transports": ["websocket"] });
    var socket = io.connect("http://127.0.0.1:5000/websocket", {"transports": ["websocket"]}); 
    // + document.domain + ":" + location.port + "/websocket"); //, {"transports": ["websocket"] });

  socket.on('connect',    function()     {       add_event(Date.now(), "Websocket connected..."); });
  socket.on('disconnect', function()     {       add_event(Date.now(), "Websocket disconnected..."); });
  socket.on("message",  function(data) {    
		console.log(data);
        if (data.stamp) {
          txt = (data.sender == "_Anonymous") ? "" : ("<b>From:</b> " + data.sender);
          if (data.node_id)
            txt += " <b>NodeID:</b> " + data.node_id;
          if (data.value || data.value_id)
            txt += " <b>Value:</b> " + data.value + " <b>ValueID:</b> " + data.value_id;
  		  add_event(data.stamp*1000, txt, data.event_type);
        } else
          add_event(Date.now(), data.msg);
	});

 	$( "#menu" ).menu({
         select: function( event, ui ) {
 				 cmd = ui.item[0].firstChild.innerText;
 				}
 		});
 	
  $( "#startup" ).controlgroup();
  $( "#startup" ).controlgroup({"direction": "vertical"});

  $( "#menu" ).on( "menuselect", function( event, ui ) {} );

  $( "#init_device" ).on({
 	  click: function() {
			var opts = new Object({device: inp.val()});
 			post_opts(null, null, null, opts);
     }
  });

  generic_ajax("POST", "/net/ctrl/action/device", {}, function(res) {
    set_init_button(res.error == undefined || res.state == 0);
  });

});
