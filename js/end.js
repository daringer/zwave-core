"use strict";

$("#event_grid").jsGrid({
	width: "50%",
	height: "150px",

	inserting: false,
	editing: false,
	sorting: true,
	paging: false,
	autoload: false,
  filtering: false,

	controller: {
		loadData: function() {
			var d = $.Deferred();
			$.ajax({
				url: "/net/signals/latest/20",
			}).done(function(response) {
				d.resolve(response)
			});
			return d.promise();
		}
	},
	fields: [
		{ name: "stamp",     type: "number",                    visible: false },
		//{ name: "Date",      type: "text",                    width: 32 },
		{ name: "Time",      type: "text",                      width: 40 },
		{ name: "EventType", type: "text", title: "Event Type", width: 55 },
		{ name: "Content",   type: "text",                      width: 220 },
	]
});

$("#node_grid").jsGrid({
    width: "100%",
	  height: "250px",

    inserting: false,
    editing: false,
    sorting: true,
    paging: false,
    autoload: false,
    filtering: false,

    //rowRenderer: function(item) {
    //    return $("<tr>").addClass("custom-row").append($("<td>").append(item.Name));
    //},

  fields: [
    { name: "node_id",            title: "ID",                  type: "text", readOnly: true, width: 30 },
    { name: "name",               title: "Name",                type: "text", width: 30},
    { name: "location",           title: "Loc",                 type: "text", width: 40 },
    { name: "query_stage",        title: "Query Stage",         type: "text", width: 40 },
    { name: "type",               title: "Type (Specific)",     type: "text", readOnly: true },
    //{ name: "specific",           title: "Sub-Type",            type: "text", readOnly: true, width: 45 },  //# "specific"
    { name: "product_name",       title: "Product Name",        type: "text", readOnly: true },
    { name: "product_type",       title: "Product Type (ID)",   type: "text", readOnly: true },
    //{ name: "product_id",         title: "Product ID",          type: "text", readOnly: true },
    { name: "manufacturer_name",  title: "Maker Name (ID)",     type: "text", readOnly: true },
    //{ name: "manufacturer_id",    title: "Maker ID",            type: "text", readOnly: true },
    { name: "ctrl",               title: "",                    type: "text", readOnly: true},
  ]
    //{ name: "Manufacturer Name", type: "checkbox", title: "Is Married", sorting: false },
    //{ name: "Product Name",      type: "select", width: 200 }, //items: countries, valueField: "Id", textField: "Name" },
	  //{ name: "Name",              type: "text",   width: 150 }, //, validate: "required" },
});

//$("#node_details_grid").jsGrid({
function assemble_grid(my_fields) {
	return Object({
    width: "20%",
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

    fields: my_fields
  });
	//{ name: "Manufacturer Name", type: "checkbox", title: "Is Married", sorting: false },
          //{ name: "Product Name",      type: "select", width: 200 }, //items: countries, valueField: "Id", textField: "Name" },
	//{ name: "Name",              type: "text",   width: 150 }, //, validate: "required" },
}
