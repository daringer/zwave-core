function DumpObject(obj, descent=false)
{
  var od = new Object;
  var result = "";
  var len = 0;

  for (var property in obj)
  {
    var value = obj[property];
    if (typeof value == 'string')
      value = "'" + value + "'";
    else if (typeof value == 'object')
    {
      if (value instanceof Array)
      {
        value = "[ " + value + " ]";
      }
      else
      {
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

function add_event(stamp, text) {
	return $("#event_grid").jsGrid("insertItem", {
		stamp: stamp, 
		time: Date(stamp).slice(0, 24) + "::" + stamp.toString().slice(-3),
		content: text
	}).done(function() {
		$("#event_grid").jsGrid("sort", {field: "stamp", order: "desc"});
	});
};

function generic_ajax(type, url, data, success_func) {
	return $.ajax({ 
		type: type, 
		url: url, 
		data: data, 
		error: function() {
			add_event(Date.now(), "Failed: '" + type + "' request to: '" + url + "' with data: " + DumpObject(data));
		},
		success: success_func
	});
};

function post_opts(resp=null, status=null, xhr=null, opts) {
 	return generic_ajax("POST", "/net/opts", opts, function() {
 		add_event(Date.now(), "Success adding option(s): " + DumpObject(opts));
 	}).done(post_net_start);
};

function post_net_start(resp=null, status=null, xhr=null) {
	return generic_ajax("POST", "/net/action/start", {}, function() {
 		add_event(Date.now(), "Success initing controller");
 	  var inp = $("#device_path");
    var but = $("#init_device");
 		if (inp.prop("disabled")) {
 			inp.prop("disabled", false);
 			but.html("init device")
 		} else {
 			inp.prop("disabled", true);
 			but.html("close device");
 		}
 	});
};

$( function() {
 	var inp = $("#device_path");
 	var but = $("#init_device");
 	var evts = $("#event_grid");
 	inp.val("/dev/ttyACM0");

  var socket = io.connect("http://" + document.domain + ":" + location.port + "/websocket");
  /*socket.on("my response", function(msg) {
      $("#log").append("<p>Received: " + msg.data + "</p>");
  });*/
  /*$("form#emit").submit(function(event) {
      socket.emit("my event", {data: $("#emit_data").val()});
      return false;
  });*/
  /*$("form#broadcast").submit(function(event) {
      socket.emit("my broadcast event", {data: $("#broadcast_data").val()});
      return false;
  });*/ 

	socket.on("event_msg", function(msg) {
		add_event(Date.now(), msg);
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
 			
 			post_opts(null, null, null, opts); //.then(function() { 
				//alert(123); 
			//});

      /* $.ajax({
         type: "POST",
         url: "/net/opts",
         //headers: {"Authorization" : "OAuth " + sessionId},
         //crossDomain : true,
         data: opts,
         //dataType: 'json',
         success: function (resp, status, xhr) {
 					add_event(Date.now(), txt, function() {
 					  evts.jsGrid("sort", {field: "stamp", order: "desc"});
 						if (!init_mode) {
 							inp.prop("disabled", false);
 							but.html("init device")
 						} else {
 							inp.prop("disabled", true);
 							but.html("close device");
 						}
 					});
 					$.ajax({
 						type: "POST",
 						url: ("/net/action/start",
 						success: function(resp, status, xhr) {
 					  txt = (inp.prop("disabled")) ? "successfully closed device" : "successfully init opening device"
 							add_event(Date.now(), "success initing device
 						},
 						error: function(req, status, error) {

 						}
 					});
         },
         error: function (req, status, error) {
 					add_event(Date.now(), "failed set option: device", function() {
 					  evts.jsGrid("sort", {field: "stamp", order: "desc"});
 					});
         }
       });*/
     }
  });
});
