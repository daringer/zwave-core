# Z-Wave Core - Complete, flexible, pluggable
Access to your network from any automation with REST or publish your network as MQTT!

Or you are simply looking to (finally) replace **ozwcp** to maintain your network hassle-free? here you go!

## Quickstart

more today


## The Vision


## Frontend(s) / Interoperability


## Status


## Documentation



## Realizations



## Contribute


## Micro-documentation (`/toc` output)

/frontend                                HEAD,GET			               frontend
/net                                     HEAD,GET		                 netinfo 
/net/action/action                       POST			                   netaction 
/net/actions                             HEAD,GET			               available_net_actions
/net/ctrl/action/action                  POST							           ctrlaction 
/net/ctrl/actions                        HEAD,GET                    available_ctrl_actions
/net/opts                                GET,HEAD,DELETE,PATCH,POST  options 
/net/signals                             HEAD,GET		  	 	 	 	 	 	 	 list_signals
/node/<int:node_id>                      GET,HEAD,PATCH              node 
/node/<int:node_id>/action/action        POST		                     node_action 
/node/<int:node_id>/value/<int:value_id> POST,HEAD,GET				       nodevalue 
/nodes                                   HEAD,GET			               nodelist
/static/filename         			           HEAD,GET	                   static 
/static/js/<string:path>                 HEAD,GET 	                 frontend_static
/static/js/<string:path>                 HEAD,GET                    frontend_static
/toc                                     HEAD,GET			               list_routes


