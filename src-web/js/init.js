"use strict";

function add_node(node) {
		/* find 'someone' to be asked for all these html-ids */
	  //var node_link_id = "node_details_link_" + node.node_id;

		var my_node = gob.manager.new_node(node);

		/* @todo, those fields exists twice :/ */
    return $("#node_grid").jsGrid("insertItem", {
        "node_id": node.node_id,
        "name": node.name,
        "location": node.location,
			  "query_stage": node.query_stage,
        "type": node.type, // + " (" + node.specifc + ")",
        //"specific": node.specific,
        "product_name": node.product_name,
        "product_type": node.product_type + " : " + node.product_id,
        //"product_id": node.product_id,
        "manufacturer_name": node.manufacturer_name + " (" + node.manufacturer_id + ")",
        //"manufacturer_id": node.manufacturer_id,
			  //"ctrl": "<a href=# id=\"" + node_link_id + "\">show</a>"
    }); /*.then(function() {
	  	$("#" + node_link_id).click(node.node_id, function(ev) {
	  		gob.manager.node_all_details(ev.data, add_detail, add_group,
					add_node_action, add_node_prop, add_stats).then(function() {
						$(document).trigger("Frontend::UpdatedDetails");
				});
		  });
    });*/
}

function add_node_action(node_id, act_id) {
	var key = `op_${node_id}_${act_id}`;
	var desc = act_id.replace(/_(.)/g, (x) => " " + x[1].toUpperCase());
	desc = desc[0].toUpperCase() + desc.substr(1);
	var html = `
	  <div class=action_node_item>
  		<div class=action_node_link_box>
		    <a href=# class=action_node_link id=${key}_link>${desc}</a>
		  </div>
		</div><hr>`;
	$("#node_details_actions_content").append(html);
  $("#" + key + "_link").click({node_id: node_id, action: act_id}, function(ev) {
		gob.manager.node_action(ev.data.node_id, ev.data.action);
	});
}

function add_node_prop(node_id, prop_key, prop_value) {
	/* avoid adding unwanted here as properties */
	if(["groups", "values", "stats", "actions"].findIndex((x) => (x == prop_key)) > -1)
		return;

	var node = gob.manager.get_node(node_id);
	prop_value = prop_value.toString().split(",").join(", ").trim().replace(/  /g, "");

	/* find 'someone' (central class/obj whatsoever) to be asked for all these html-ids */
	var key = `node_prop_${node_id}_${prop_key}`;
	var html = `
	  <div id=${key} class=prop_data_box>
	    <div class=prop_data_label>
		    <label for=${key}>${prop_key}</label>
			</div>
      <span name=${key} id=${key}_data class=prop_data>${prop_value}</span>
	  	</div>`;

  $("#node_details_props_content").append(html);
}

function add_stats(node_id, stat_key, stat_value, target_detail) {
	var node = gob.manager.get_node(node_id);
	var key = `node_${target_detail}_${node_id}_${stat_key}`;

	if (stat_key == "lastReceivedMessage") {
		stat_value = stat_value.map((num) => num.toString(16).toUpperCase().lpad("0", 2));
		let out = new Array();
		for (var row=0; row<16; row++)
				out.push(stat_value.slice(row*8, (row+1)*8).join(" ") +
					  "<span class=hex_spacer>&nbsp;</span>" +
						stat_value.slice((row+1)*8, (row+2)*8).join(" "));

		stat_value = out.join("<br />");
		stat_value = stat_value.slice(0, -6);
		stat_value = stat_value.padEnd(stat_value.length+60, "&nbsp;");
		stat_value = "<span class=hex_msg>" + stat_value + "</span>";
	}

	var html = `
	  <div id=${key} class=prop_data_box>
	    <div class=prop_data_label>
		    <label for=${key}>${stat_key}</label>
			</div>
      <span name=${key} id=${key}_data class=prop_data>${stat_value}</span>
	  	</div>`;

  $(`#node_details_${target_detail}_content`).append(html);

}

function add_group(node_id, group) {
	var node = gob.manager.get_node(node_id);
	var num_items = Object.keys(group.associations).length;
	var key = `group_${node_id}_${group.index}`;
	var html = `<div id=${key} class=group_data_box>
			<div class=group_data_label>
				<label for=${key}>${group.label}</label>
				<div class=group_cur_max># ${group.cur_count} / ${group.max_count}</div>
			</div>`;

	if (Object.keys(group.associations).length > 0)
		for (var n_id in group.associations)
			html += `<div id=${key}_assoc_${n_id} class=group_data_assoc>- NodeID: ${n_id}
				<div class=group_data_assoc_icon id=${key}_assoc_${n_id}_remove>-</div>
			</div>`;

	// do not show select-dropdown and "+" icon if max assoiciations already reached here
	if (group.cur_count < group.max_count) {
		var add_select_key = key + "_assoc_add";
		var sel_cls = "group_data_assoc_add_select";
		html += `<div class=group_data_assoc_add><form name=add_to_group>
						 <select class=${sel_cls} id=${add_select_key}>
						 <option value=none>[select node_id to add]</option>`;

		for(var sub_node_id in gob.nodes)
			if (!(sub_node_id in group.associations) && sub_node_id != node_id)
				html += `<option value=${sub_node_id}>${sub_node_id}</option>`;
		html += `</select><div class=group_data_assoc_icon id=${add_select_key}_link>+</div></form></div>`;
	}

	html += "</div><hr>";

	$("#node_details_groups_content").append(html);

	if (group.cur_count < group.max_count) {
		$("#" + add_select_key + "_link").click({node_id: node_id, group_idx: group.index, select: add_select_key}, function(ev) {
			var target_node_id = $("#" + ev.data.select).val();
			/* do nothing, if no node_id is selected... */
			if (target_node_id == "none") {
				var bg_base = $("#" + ev.data.select).css("background-color");
				$("#" + ev.data.select).animate({"background-color": "#ff0000"}, 200).
					animate({"background-color": bg_base}, 500);
			} else {
				gob.manager.group_node_add(ev.data.node_id, ev.data.group_idx, target_node_id);
				gob.manager.node_update_groups(ev.data.node_id, add_group, true);
			}
		});
	}

	for (var n_id in group.associations) {
		$("#" + key + "_assoc_" + n_id + "_remove").click(
			{node_id: node_id, group_idx: group.index, target_node_id: n_id}, function(ev) {
				gob.manager.group_node_remove(ev.data.node_id, ev.data.group_idx, ev.data.target_node_id);
				gob.manager.node_update_groups(ev.data.node_id, add_group, true);
			});
	}

}

function add_detail(node_id, val) {
	var node = gob.manager.get_node(node_id);
	var desc = val.label;

	/* find 'someone' (central class/obj whatsoever) to be asked for all these html-ids */
	var key = `node_${node_id}_${val.value_id}`;
	var label_extra = `[cmd class: ${val.command_class}]`;
	var desc_add = (val.units) ? ` [${val.units}]` : "";
	var html = `
	  <div id=${key} class=val_data_box>
	    <div class=val_data_label>
		    <label for=${key}>${desc}${desc_add}</label>
		    <div class=val_data_label_extra>${label_extra}</div>
	  	</div>`;
	var change_handler = false;

	if (val.is_read_only) {
		html += `<span name=${key} id=${key}_data class=val_data>${val.fancy_data}</span>`;

	} else if (val.html_type == "select" || val.html_type == "binary") {
		if (typeof val.data_items == "object" && val.data_items instanceof Array)
		  var data_pairs = val.data_items.map((item) => [item, item])
		else
		  var data_pairs = Object.keys(val.data_items).map((key) => [key, val.data_items[key]])

		var innerhtml = data_pairs.map(function(my_val) {
			if (my_val[1] === true || my_val[1] === false || my_val[0] === false || my_val[0] === true) {
      	var opt_key = ((my_val[1] === true) ? "on" : "off" );
      	var opt_val = ((my_val[1] === true) ? "on" : "off" );
      } else {
        var opt_key = my_val[0];
        var opt_val = my_val[1];
			}
      var out = `<option value='${opt_key}'` + ((opt_val == val.data) ? " selected=selected " : "");
      out += ">" + opt_val + "</option>";
      return out;
		});
		html += `<select name=${key} id=${key}_data class=val_data>${innerhtml}</select>`;
		change_handler = true;

	} else if (val.html_type == "input") {
		var minmax = "";
		if (val.min)
			minmax += `min: ${val.min} `;
		if (val.max)
			minmax += `max: ${val.max}`;
		html += `<input name=${key} id=${key}_data value=\"${val.fancy_data}\" class=val_data />`;
		if (minmax != "")
			html += `<span class=val_data_minmax>${minmax}</span><br />`;
		html += `<span class=val_data_extra_text>${val.data_items}</span>`;
		change_handler = true;

	} else
		html += `Cannot render: html_type: ${val.html_type} value_id: ${val.value_id} value: ${val.data} / ${val.data_items}`;

	html += "</div><hr>";

  var sel = $("#node_details_" + val.genre.toLowerCase() + "_content");
	sel.append(html);

	// do callback connection, if <select> or <input> field is there
	if (change_handler)
		$("#" + key + "_data").change({node_id: node.node_id, value_id: val.value_id}, function(ev) {
			var idkey = `#node_${ev.data.node_id}_${ev.data.value_id}_data`;
			$( document ).trigger("Frontend::ValueChanged", ev.data);
			gob.manager.set_node_value(ev.data.node_id, ev.data.value_id, $(idkey).val());
		});
	return html;
}


/**                          **/
/** Entrypoint follows here: **/
/**                          **/

var config = {
	device_path: "/dev/ttyACM0",
	config_path: "/etc/openzwave",
	log_path: "OZWLog.log",
  user_path: "."
};


// gob == Global State Object
var gob = {
    // nodes @TOOD: bad!
	  nodes: {},
    // keep device path @TOOD: why? manager? config?
  	device_path: null,
	  // mananger object
	  manager: null,
		// network object @TODO: why? manager should have it, too!
	  network: null,
	  // activate debug mode, mainly IO.log() will be replaced with IO.debug()
    debug: true
};



$( function() {

	class _inps {
		get device_path() { return $("#device_path"); }
		get user_path()   { return $("#user_path"); }
		get config_path() { return $("#config_path"); }
		get log_path()    { return $("#log_path"); }

		map(func) {
			return [this.device_path, this.user_path, this.config_path, this.log_path
						 ].map(elem => func(elem));
		}
	};

	class _buttons {
		get ctrl_inc()     { return $("#ctrl_include"); }
		get ctrl_inc_sec() { return $("#ctrl_include_secure"); }
		get ctrl_cancel()  {  return $("#ctrl_cancel"); }
		get ctrl_exclude() { return $("#ctrl_exclude"); }
		get ctrl_heal()    { return $("#ctrl_heal"); }
		get ctrl_remove_failed() { return $("#ctrl_remove_failed"); }
		get get_state()    { return $("#get_state"); }
		get write_config() { return $("#write_config"); }
		get net_start()    { return $("#device_on"); }
		get net_stop()     { return $("#device_off"); }
	};

	// "easyier" access for the buttons and input-fields
	// (@TODO: really? nothing better?)
	var buts = new _buttons();
	var inps = new _inps();

 	var evts = $("#event_grid");

	// global objects
	gob.manager = new AjaxManager("", IO);
	gob.network = new Network(IO);

	// start / stop network button handlers:
  buts.net_start.click(function() {
      var opts = new Object({
				device:      inps.device_path.val(),
				user_path:   inps.user_path.val(),
				config_path: inps.config_path.val(),
				log_file:    inps.log_path.val()
			});
      $.when(gob.manager.net_opts(opts).done(() => gob.manager.net_action("start")));
  });
  buts.net_stop.click( () => gob.manager.net_action("stop") );


	// all static buttons, @TODO, @TODO
	//var not_impl = function() { alert("NOT IMPLEMENTED");  };

	buts.ctrl_inc.click(function()           { gob.manager.net_ctrl_action("add_node"); } );
	buts.ctrl_inc_sec.click(function()       { gob.manager.net_ctrl_action("add_secure_node"); } );
	buts.ctrl_exclude.click(function()       { gob.manager.net_ctrl_action("remove_node"); } );
	buts.ctrl_cancel.click(function()        { gob.manager.net_ctrl_action("cancel_command"); } );
	buts.ctrl_heal.click(function()          { gob.manager.net_action("heal"); } );

	// actually does not belong here, but in the node list/jsgrid view
	//buts.ctrl_remove_failed.click(function() { gob.manager.net_action("remove_failed_node"); } );
	//buts.ctrl_remove_failed.click(function() { gob.manager.net_action("remove_failed_node"); } );

	buts.get_state.click(function()          {
			gob.manager.net_action("state");
	});

	buts.write_config.click(() => gob.manager.net_action("write_config"));

	// fill defaults into input-fields
	inps.map(elem => elem.val(config[elem.attr("id")]));

	//
	// --- now some event handlers ---
	// ---     ZWave triggered     ---
	//
	// network starting up, triggered once
	$( document ).on("ZWave::NetworkStarted", function(data) {
		gob.manager.post("/net/ctrl/action/device", {},
			(res) => {
				gob.network.setup();
				gob.device_path = res.data.returned;
				inps.map(elem => elem.prop("disabled", true));
				buts.net_start.prop("disabled", true);
				buts.net_stop.prop("disabled", false);
				gob.manager.map_nodes(add_node);

				//// removed, as somehow unused ?! @TODO, what's up here? feature?
				// var ctrl = Controller(gob.net, IO);
				// ctrl.setup(gob.net);
			});
	});
	// network goes down, triggered once
	$( document ).on("ZWave::NetworkStopped", function(data) {
		gob.device_path = null;
		inps.map(elem => elem.prop("disabled", false));
		buts.net_start.prop("disabled", false);
		buts.net_stop.prop("disabled", true);
		gob.network.teardown();
	});

	// value is added to node, important for a perfect startup
	$( document ).on("ZWave::ValueAdded", function(ev, data) {
		console.log("ValueAdded NOT YET HANDLED!!!");
	});

	// node value changed sig-handler...
	$( document ).on("ZWave::ValueChanged", function(ev, data) {

		var base_id = `#node_${data.node_id}_${data.value_id}`;
		var data_id = base_id + "_data";
		var node = gob.manager.get_node(data.node_id);

		// only fade grey, if no change, on change: fade to red
		//var to_col = "#ff0000";
		var to_col = "#666666";
		var new_data = node.update_value(data.value_id, data.value_data);
		$(data_id).val(new_data);

		// housekeeping
		var bg_base = $(base_id).css("background-color");
		var bg_data = $(data_id).css("background-color");
		// bling, bling
		$(base_id).animate({"background-color": to_col}, 200).
				animate({"background-color": bg_base}, 500);
		$(data_id).animate({"background-color": to_col}, 200).
				animate({"background-color": bg_data}, 500);
	});

	// ---   Frontend triggered    ---
	//
	// handle user-based value change
	$( document ).on("Frontend::ValueChanged", function(ev, data) {

		var base_id = `#node_${data.node_id}_${data.value_id}`;
		var data_id = base_id + "_data";
		var to_col = "#ff00ff";
		// housekeeping
		var bg_base = $(base_id).css("background-color");
		var bg_data = $(data_id).css("background-color");
		// bling, bling
		$(base_id).animate({"background-color": to_col}, 200).
				animate({"background-color": bg_base}, 500);
		$(data_id).animate({"background-color": to_col}, 200).
				animate({"background-color": bg_data}, 500);
	});

	// details layout housekeeping
	$( document ).on("Frontend::UpdatedDetails", function(ev) {
		var fields = ["basic", "user", "system", "config", "groups",
							    "actions", "props", "stats", "ctrlstats"];
		var keys = fields.map((field) => `#node_details_${field}_content`);

		// hide empty detail-blocks
		keys.forEach((my_id) => {
			var sel = $(my_id);
			if (sel.html().trim() == "")
				sel.parent().hide();
			else
				sel.parent().show();
		});
	});

	// init and connect to websocket-based events
	var socket = io.connect("/websocket", {"transports": ["websocket"]});

	// ---   WebSocket triggered    ---
	//
	socket.on('connect',    function()     { IO.log("Websocket connected successfully");   });
	socket.on('disconnect', function()     { IO.log("Websocket disconnected successfuly"); });

	// main non-request a.k.a. push-based server-to-client communication path
	// each ZWave-signal and other pushed messages arrive here
	socket.on("message",    function(data) {
		// each 'signale' triggers another JS event
		$( document ).trigger( "ZWave::" + data.signal, data);
		
		var msg = Object.keys(data).map((key) => `${key}: ${data[key]}`);

		if (!gob.debug)
			IO.log(msg, Date.now(), data["signal"]);
		else
			IO.debug(msg);

	});

  // jquery-ui init(s)
  $( ".top_box" ).controlgroup();
  $( ".top_box" ).controlgroup({"direction": "vertical"});

  // check, if the network is up or down and emit a signal accordingly
  gob.manager.generic_ajax("GET", "/net", {}, function(res) {
    if (typeof res.error !== "undefined" ||
	      (res.states && typeof res.states.net !== "undefined" && res.states.net == 0))
	    $(document).trigger("ZWave::NetworkStopped");
    else
	    $(document).trigger("ZWave::NetworkStarted");
  });
	// on "startup", do housekeeping in details layout
	$(document).trigger("Frontend::UpdatedDetails");

	// @TODO: not functional, thus hidden...
	$("#zwave_config_log").hide();

});
