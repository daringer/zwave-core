"use strict";

$("#event_grid").jsGrid({
	width: "50%",
	height: "150px",

	inserting: false,
	editing: false,
	sorting: true,
	paging: true,
	autoload: false,
	filtering: false,
	pageSize: 50,

	// still sooner or later a server-based event-log would not be bad!
	/*controller: {
		loadData: function() {
			var d = $.Deferred();
			$.ajax({
				url: "/net/signals/latest/20",
			}).done(function(response) {
				d.resolve(response)
			});
			return d.promise();
		}
	},*/
	fields: [
		{ name: "stamp",     type: "number",                    visible: false },
		//{ name: "Date",      type: "text",                    width: 32 },
		{ name: "Time",      type: "text",                      width: 40 },
		{ name: "EventType", type: "text", title: "Event Type", width: 55 },
		{ name: "Content",   type: "text",                      width: 220 },
	],

	/* hack to insert at top of grid ... */
	onItemInserting: function(args) {
	  args.cancel = true;
	  var grid = args.grid;
          grid.option("data").unshift(args.item);
          grid.refresh();
	}

});

$("#node_grid").jsGrid({
	width: "100%",
	height: "250px",

	inserting: false,
	editing: true,
	sorting: true,
	paging: false,
	autoload: false,
	filtering: false,

	//rowRenderer: function(item) {
	//    return $("<tr>").addClass("custom-row").append($("<td>").append(item.Name));
	//},

	fields: [
		{ name: "node_id",            title: "ID",                  type: "text", editing: false, readOnly: true, width: 30 },
		{ name: "name",               title: "Name",                type: "text", width: 30 },
		{ name: "location",           title: "Loc",                 type: "text", width: 40 },
		{ name: "query_stage",        title: "Query Stage",         type: "text", editing: false, readOnly: true, width: 40 },
		{ name: "type",               title: "Type (Specific)",     type: "text", editing: false, readOnly: true },
		{ name: "product_name",       title: "Product Name",        type: "text", editing: false, readOnly: true },
		{ name: "product_type",       title: "Product Type (ID)",   type: "text", editing: false, readOnly: true },
		{ name: "manufacturer_name",  title: "Maker Name (ID)",     type: "text", editing: false, readOnly: true },
		{ name: "ctrl",               title: "",                    type: "control", editButton: true, deleteButton: false, width: 25},
	],

	onItemEditing: function(args) { },

	onItemUpdating: function(args) {
		var node_id = args.item.node_id;
		var new_name = args.item.name;
		var new_loc = args.item.location;

		var node = gob.manager.get_node(node_id);
		node.set_field("name", new_name);
		node.set_field("location", new_loc);
	},

	rowClick: function(args) {
		var node_id = args.item.node_id;
		gob.manager.node_all_details(node_id, add_detail, add_group,
			add_node_action, add_node_prop, add_stats).then(function() {
				$(document).trigger("Frontend::UpdatedDetails");
			});
	}


});


