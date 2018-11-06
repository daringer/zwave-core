# Z-Wave Core - Complete, flexible, pluggable
Access to your network from any automation with REST or publish your network as MQTT!

Or you are simply looking to (finally) replace **ozwcp** to maintain your network hassle-free? here you go!


**classic warning:** this project is in active development, so theoretically there are chances that
things go wrong and in the very, very unlikely but possible case there might be the chance that
your nodes get somehow excluded or your controller might get hard-resettet.

Currently explicitly neither of both functionalities are included currently inside the frontend.
The REST API already supports it technically.

## Quickstart

1) get python > 3.5
2) install the following packages (using pip)

	 * eventlet
	 * flask
	 * flask_restful
	 * flask_socketio
	 * jinja2
	 * python-openzwave
	 * pydispatch

3) ensure you know where your openzwave configurationdirectory is to be found,
   for me it simply is `/etc/openzwave`

4) check if your controller serial device (something like `/dev/ttyACM0`) is writeable

5) simply execute `start.py` from within the project directory using python:
```python start.py```

6) start a browser and visit: [127.0.0.1:5000/frontend](http://127.0.0.1:5000/frontend)

7) in the top left, enter your configuration directory and `device path`, press the `on`
   button below `network` watch the events flowing while initializeations are done...


## The Vision

* first public release to github yesterday, wanted to have it on a certain level first

* REST API already exposes nearly the full ZWave stack
  (scenes missing, assoc groups adding/removing nodes, some other minor stuff)

* a web frontend (ozcwp replacement) making use of the REST API and websocket-based push
  to not miss a single signal, overall it's "ok", worth calling it ozcwp replacement with a
	pretty long list of details to be done

* finally expose any ZWave device via MQTT, use the frontend to pick/combine
  whatever is needed and publish it

## Frontend(s) / Interoperability

## Status

## Documentation

## Realizations

## Contribute

## Screenshots

---------------------

![full node view, any possible detail on one screen, directly editable, instant feedback, websocket driven event log in the top right corner](https://github.com/daringer/image_dump/blob/master/zwave-core-screen1.png)

-----------------------

![controller view, less configuration, full ajax frontend (oczwp-replacement), full REST-api already available](https://github.com/daringer/image_dump/blob/master/zwave-core-screen2.png)

-----------------------

## REST API - Micro-documentation (`/toc` output)

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


