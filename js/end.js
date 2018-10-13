"use strict";

$("#event_grid").jsGrid({
	width: "100%",
	height: "400px", 

	inserting: false,
	editing: false,
	sorting: true,
	paging: true,
	autoload: false,
    filtering: false,

	controller: { 
		loadData: function() {
			var d = $.Deferred();
			$.ajax({
				url: "/net/signals/latest/20",
				//dataType: "json"
			}).done(function(response) {
				d.resolve(response)
			});
			return d.promise();
		}
	},
	fields: [
		{ name: "stamp",     type: "number",                    visible: false },
		{ name: "Date",      type: "text",                      width: 32 },
		{ name: "Time",      type: "text",                      width: 40 },
		{ name: "EventType", type: "text", title: "Event Type", width: 80 },
		{ name: "Content",   type: "text",                      width: 220 },
	]
});

$("#node_grid").jsGrid({
    width: "100%",
	height: "200px", 

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
    { name: "node_id",            title: "Node ID",             type: "text", readOnly: true },
    { name: "name",               title: "Name",                type: "text" }, 
    { name: "location",           title: "Location",            type: "text" },
    { name: "type",               title: "Type",                type: "text", readOnly: true },
    { name: "specific",           title: "Specific Type",       type: "text", readOnly: true },
    { name: "product_name",       title: "Product Name",        type: "text", readOnly: true }, 
    { name: "product_type",       title: "Product Type",        type: "text", readOnly: true }, 
    { name: "product_id",         title: "Product ID",          type: "text", readOnly: true }, 
    { name: "manufacturer_name",  title: "Manufacturer Name",   type: "text", readOnly: true },
    { name: "manufacturer_id",    title: "Manufacturer ID",     type: "text", readOnly: true }, 
  ]
          //{ name: "Manufacturer Name", type: "checkbox", title: "Is Married", sorting: false },
          //{ name: "Product Name",      type: "select", width: 200 }, //items: countries, valueField: "Id", textField: "Name" },
	//{ name: "Name",              type: "text",   width: 150 }, //, validate: "required" },
});
