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

3) ensure you know where your openzwave configuration directory is to be found,
   for me it simply is `/etc/openzwave`

4) check if your controller serial device (something like `/dev/ttyACM0`) is writeable

5) if you would like zwave-core to use an already existing `zwcfg_<home_id>.xml` openzwave
   cache file, make sure you have its path (i.e., the containing directory) noted

6) simply execute `start.py` from within the project directory using python:
```python start.py```

7) start a browser and visit: [127.0.0.1:5000/frontend](http://127.0.0.1:5000/frontend)

9) in the top left, enter your the three paths you noted before:

  * configuration directory
	* `device path`
	* user path, i.e., directory containing your zwcfg<home_id>.xml`

9) click the `on` button below `network` watch the events flowing while initializeations are done

## The Vision

ZWave-core shall---as the name suggests---be the core component for the interaction with Z-Wave
devices and the network. Providing a highly transparent and accurate interface into the Z-Wave
protocol and not hiding any detail. Using a REST API this transparency is delivered in a platform
independent, easy accessible way.

A dynamic, web-based and reactive interface is exposing this REST API to the browser, serving
as a clear window into the Z-Wave world. In order to transport the high dynamic of the Z-Wave
network, websocket-based push is a must allowing the receiver side to not miss any information
within the network with the smallest possible latency.

In contrast to this plain, bare-metal approach the major distinguishing feature will be the MQTT
layer, which introduces a abstraction layer between any home-automation system and the Z-Wave
network in order to seperate what does not belong together: physical and functional layers.
While the former is deployable standalone, without prior knowledge of the surroundings despite
the Z-Wave network itself, the latter has the freedom to not care about the physical layer at all
and focus on the functional, end-user focussed challenges. So, in simple words zwave-core provides
a Z-Wave to IP bridge allowing simplicity in Z-Wave management bridging the gap between WiFi and
the ISM band.

### REST API

| URL                                      |  Methods                  | Description
| ----                                     |  -------                  | -----------
| /net                                     |  GET                      | ...
| /net/actions                             |  GET                      |
| /net/action/action                       |  POST                     |
| /net/ctrl/actions                        |  GET                      |
|                                          |                           |
| /net/ctrl/action/action                  |  POST                     |
| /net/opts                                |  GET,DELETE,PATCH,POST    |
| /net/signals                             |  GET                      |
|                                          |                           |
| /nodes                                   |  GET                      |
| /node/<int:node_id>                      |  GET,PATCH                |
| /node/<int:node_id>/value/<int:value_id> |  GET,POST                 |
| /node/actions                            |  GET                      |
| /node/<int:node_id>/action/action        |  POST                     |
|                                          |                           |
| /toc                                     |  GET                      |

### Browser Frontend

### MQTT

Not started yet, but soon it will be ready.(tm)

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


