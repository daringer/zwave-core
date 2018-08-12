$("#event_grid").jsGrid({
        	width: "100%",
					height: "200px", 

					inserting: false,
					editing: false,
					sorting: true,
					paging: true,
					autoload: false,

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
						{ name: "stamp",   type: "number", visible: false },
						{ name: "time",    type: "text", width: 100 },
						{ name: "content", type: "text", width: 300 },
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

					  controller: {
								loadData: function() {
									var d = $.Deferred();
									$.ajax({
										url: "/nodes", 
										//dataType: "json"
								  }).done(function(response) {
										d.resolve(response.nodes);
									});
									return d.promise();
								}
						},
						
            //data: nodes,
  
            fields: [
                { name: "(Node)ID",          type: "number", width: 100 },
   							{ name: "Name",              type: "text",   width: 150 }, 
                { name: "Location",          type: "text",   width: 200 },
   							{ name: "Product Name",      type: "text",   width: 200 }, 
  							{ name: "Manufacturer Name", type: "text",   width: 200 },
							  { type: "control",           width: 35 },
            ]
            //{ name: "Manufacturer Name", type: "checkbox", title: "Is Married", sorting: false },
   					//{ name: "Product Name",      type: "select", width: 200 }, //items: countries, valueField: "Id", textField: "Name" },
   					//{ name: "Name",              type: "text",   width: 150 }, //, validate: "required" },
        });
