"use strict";
class AjaxManager {
  constructor (base_url, zw_obj)  {
		this.base_url = base_url;
		this.zw_obj = zw_obj;
	}

	log(txt, stamp, log_type) {
		return IO.log(txt, stamp, log_type);
	}

	/** generic ajax call short-cut */
	generic_ajax(type, url, data, success_func=null) {
		var base_msg = `${type} request to: <b>'${url}'</b>`;

		if (data && Object.keys(data).length > 0)
			base_msg += " with data: " + DumpObject(data);
		var log = this.log;
		var self = this;
		var func_success = this.generic_return_handler.bind(self);
		var func_error =  this.generic_error_handler.bind(self);
		var err_func = function(ret) { return func_error(ret, url, log);	};

		var ret = $.ajax({
			type: type,
			url: url,
			data: data,
			error: err_func,
			success: success_func
		});

		// finally apply generic return handler to anything that was requested...
		return ret.then((ret) => {
			if ("error" in ret)
				return func_error(ret, url, log);
			else
				return func_success(ret, url, log);
		});
	}

	generic_error_handler(ret, url, _log) {
		var msg = (ret.msg) ? ` msg: ${ret.msg}` : "";
		//var errcode = (typeof ret.error !== "undefined") ? ` error-code: ${ret.error}` : "";
		var errcode = (ret.error) ? ` error-code: ${ret.error}` : "";
		_log(`error api-call: ${url}${errcode}${msg}`, null, "err");
	}

	/** generic ajax return handler */
	generic_return_handler(ret, url, _log) {
		var base_desc = "<b>'" + url + "'</b>";

		var out = "";
		if ("error" in ret) {
			out = `error api-call: ${url} error-code: ${ret.error} msg: ${ret.msg}`;
		  _log(out, null, "err");

		} else if ("data" in ret) {
			if (ret.data.returned == null)
				out = "n/a";
			else if (typeof ret.data.returned == "object") {
				var keys = Object.keys(ret.data.returned);
				var dct = ret.data.returned;
				out = keys.map(key => (key.toString() + ": " + dct[key].toString())).join(", ");
			} else
				out = ret.data.returned.toString();
			out = `${base_desc} api-call finshed successfully`;
			_log(out);

		} else {
			out = `${base_desc} without error, message: ${ret.msg}`;
			_log(out);
		}
		return out;
	}

	/** easy access get/post ajax calls */
	get(url, data, success_func=null) {
		return this.generic_ajax("GET", url, data, success_func );
	}
	post(url, data, success_func=null) {
		return this.generic_ajax("POST", url, data, success_func );
	}

  map_nodes(cb_func) {
		var log = this.log;
		return this.get("/nodes", {}, function(ret) {
			log("Retrieving all nodes from server...");
			$("#node_grid").jsGrid("option", "data", []);
			return ret.data.map(cb_func);
		});
	}

	net_opts(opts) {
		var log = this.log;
			return this.post("/net/opts", opts, function() {
        if (!$("#device_path").prop("disabled"))
            log("Success adding option(s): " + DumpObject(opts));
 			});
	}

	node_action(node_id, act) {
		return this.post("/node/" + node_id + "/action/" + act, {});
	}

	net_action(act) {
		return this.post("/net/action/" + act, {});
	}

	net_ctrl_action(act, kw_args) {
		kw_args = (typeof kw_args == "undefined") ? {} : kw_args;
		return this.post("/net/ctrl/action/" + act, kw_args);
	}

 	get_node(node_id) {
	  /* Below action on our database bound to ajax */
	  /* @TODO: These should go into seperate class, getting AjaxManager as member
 	       to call all these from within the NodeManager */
	  	if (!(node_id in gob.nodes))
  			gob.nodes[node_id] = new Node(node_id);
	  	return gob.nodes[node_id];
	}

	new_node(node) {
		/* add node to cache from server json-node */
		if (node.node_id in gob.nodes)
				console.log(`node_id: ${node.node_id} exists, updating`);
		var out = this.get_node(node.node_id);
		out.update_from_json({info: node});
		return out;
	}

	set_node_value(node_id, value_id, new_val) {
		var postdata = {data: new_val};
		var log = this.log;
		this.post("/node/" + node_id + "/value/" + value_id, postdata, function (ret) {
			log(`Node: (${node_id}) uid: [${value_id}] set to: ${new_val}`);
		});
	}

	node_all_details(node_id, cb_add_detail, cb_add_group, cb_add_action, cb_add_prop, cb_add_stat) {
		var obj_this = this;
		return this.get("/node/" + node_id, {}, function (ret) {
			/* all node details == all available node values */
			var node = obj_this.get_node(node_id);
			node.update_from_json(ret.data);

			var fields = ["basic", "user", "system", "config", "groups", "actions", "props", "stats"];

			fields.forEach(
				(field) => $("#node_details_" + field + "_content").html(""));

			Object.keys(node.values).forEach(
				(value_id) => cb_add_detail(node_id, node.values[value_id]));

			ret.data.actions.forEach(
				(act_id) => cb_add_action(node_id, act_id));

			Object.keys(ret.data.stats).forEach(
				(stat_key) => cb_add_stat(node_id, stat_key, ret.data.stats[stat_key]));

			Object.keys(node).forEach(
				(prop_key) => cb_add_prop(node_id, prop_key, node[prop_key]));

			Object.keys(node.groups).forEach(
				(grp_id) => cb_add_group(node_id, node.groups[grp_id]));

		});
	}
}

