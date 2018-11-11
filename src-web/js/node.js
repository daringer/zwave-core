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

	update_value (value_id, data) {
		var changed = false;
		if (!(value_id in this.values)) {
			IO.err(`error : ${value_id} not in node's values`);
			return changed;
		}

		if (!("data" in this.values[value_id])) {
			IO.err(`error updating value with id: ${value_id}, no 'data' member found...`);
			return changed;
		}

		var val = this.values[value_id];
		if (val.data != data) {
			//this.values[value_id].data = data;
			val.data = data;
			//@TODO: check for successful data set
			//IO.err(`set value not saved: '${data}', or not accepted, old: ${old_data}`);
			//return changed;
			IO.log(`verified newly set value: ${data}`);
			changed = true;
			this.last_updated = Date.now();
		} else
			IO.warn(`new value-data: ${data} is equal to the old one, no changes done!`);

		return changed;
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

