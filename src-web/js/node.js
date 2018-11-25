"use strict";
class Node {

	constructor (node_id) {
		this.node_id = node_id;
		this.last_updated = Date.now();

		this.values = {};
		this.groups = {};
		this.actions = {};

		this.all_field_names =  ["name", "location"];

	}

	set_field(field_name, field_value) {
		if (this.all_field_names.findIndex((f) => f == field_name) > -1)
				gob.manager.set_node_field(this.node_id, field_name, field_value);
	}

	has_value_id(value_id) {
		return (value_id in this.values);
	}

	update_value (value_id, data) {

		if (!(value_id in this.values) || (!("data" in this.values[value_id])))
			this.values[value_id] = new Object({data: null});

		if (data === true)
			data = "on";
		if (data === false)
			data = "off";

		this.values[value_id].data = data;
		this.last_updated = Date.now();
		IO.log(`set value: ${data}`);
		return data;
	}

	update_from_json (json) {
		if ("info" in json && "node_id" in json.info && json.info.node_id != this.node_id) {
			var n_id = json.info.node_id;
			IO.err(`asked to update id: ${this.node_id} with unequal id: ${n_id}, stopping`);
			return false;
		}

		if ("info" in json)
			$.extend(this, json.info);
		if ("groups" in json)
			$.extend(this.groups, json.groups);
		if ("actions" in json)
			this.actions = json.actions;
		if ("values" in json)
			this.update_values_from_json(json.values);
		this.last_updated = Date.now();
		return true;
	}

	update_values_from_json(json) {
		// (various) hacks to avoid integer overflow in JS, due to 2**53 int-limit
		// i.e., ultimately threat them as strings, but first BigInts to ensure lossless conversion
		// ... oh, an by the way: f**k you JS, what the heck!
		var keys = Object.keys(json).map(num => BigInt(num).toString());

		keys.forEach((key) => { json[key].value_id = key; });

		var fixed_vals = keys.map(k => json[k]).map(val => {
			val.fancy_data_items = new Array();
			val.html_type = null;

			if (val.type == "Bool" || val.type == "Button") {
				val.data_items = [true, false];
				val.fancy_data_items = ["on", "off"];
				val.html_type = "binary";

			} else {
				if (val.type == "Decimal" || val.type == "String" ||
					val.type == "Short"   || val.type == "Byte")
					val.html_type = "input";
				else
					val.html_type = "select";
			}

			val.fancy_data = val.data;
			return val;
		});

		//for(var i=0; i<fixed_vals.length; i++)
		for(var item of fixed_vals)
			this.values[item.value_id] = item;

		this.last_updated = Date.now();
	}
}

