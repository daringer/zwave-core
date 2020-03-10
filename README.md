**This project is closing its doors. With the advent of https://github.com/cgarwood/homeassistant-zwave_mqtt using https://github.com/OpenZWave/qt-openzwave a.k.a. `ozwdaemon` there is not much more I could wish for (let's say the stole, my idea if anyone asks :smile:). In good open-source fashion I'll better invest into these projects instead of re-inventing the wheel. It was a short, but fun ride...**

to be an archive soon

--------------------
# Z-Wave Core - Complete, flexible, pluggable


* Maintain, troubleshoot, investigate the details of your Z-Wave network
* You are simply looking to (finally) replace **ozwcp** to maintain your network hassle-free? here you go!
* Access to your network from any automation with REST or publish your network as MQTT! (not yet available)


<a href="https://www.buymeacoffee.com/daringer" target="_blank"> <img src="https://cdn.buymeacoffee.com/buttons/lato-green.png" alt="Buy Me A Coffee Or Beer" height=22></a>

The current status:
* Z-Wave backend / REST API: **beta**
* Browser Frontend: **alpha** 
* exposing your Z-Wave network as MQTT client **alpha, not for daily use, yet**

	* Activating `mqtt` (within HA) and its discovery, allows full GUI based configuration
	* Within zwave-core just run start.py once the network is ready, visit: http://<my_zwave_core_ip>:8123/mqtt

## Quickstart

0) start somewhere, e.g., `cd /tmp` 

1) `git clone git@github.com:daringer/zwave-core.git`

2) make sure you've python > 3.x installed

3) install venv using pip: `python -m pip install venv`

4) create a fresh virtual environment and activate it:
```bash
python -m venv /tmp/zwave_core_venv
source /tmp/zwave_core_venv/bin/activate
```

5) install the requirements: 
```bash
cd /tmp/zwave-core
python -m pip install -r requirements.txt
```

6) locate your essential Z-Wave files and copy them into the zwave-core directory (this makes sure that you'll change nothing within your current Z-Wave using tool):
```bash
# for example for home-assistant
cd ~/.homeassistant
cp zwcfg_0xf5b17667.xml pyozw.sqlite zwscene.xml options.xml /tmp/zwave-core/
```

7) locate (and determine) your openzwave installation (flavor), see [at openzwave](https://github.com/techgaun/python-openzwave/). For me, I prefer the system-wide as having open-zwave installed through my pacman-ager. So for me its: `/etc/openzwave`

8) check if your controller serial device (something like `/dev/ttyACM0`) is writeable

9) simply run:
```bash
cd /tmp/zwave-core
python zwave_core/start.py
```

10) start a browser and visit: [127.0.0.1:5000/frontend](http://127.0.0.1:5000/frontend)

Now to start the network, just make sure that the 4 input fields in the top left are correct.
Controller device `/dev/ttyACM0`, openzwave database directory `/etc/openzwave`, user-dir is our current workdir, where we copied the openzwave files to for safety: `.`.

Once done click "ON" in the top left corner and wait while watching the event-log being populated by the tasks the controller is executing...

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
[127.0.0.1:5000/frontend](http://127.0.0.1:5000/frontend) ...

### MQTT

There are several ways to access the zwave nodes and entities.

* `zwave/raw/<node_id>/#` will provide you an extensive list
  about all lan-devices, including c onfigs, read-only, ...
* `homeassistant/<component type (e.g., sensor)>/<node_id>/state#'` 
  will be populated  automaticly
* there will later also be the option to change how a specific
  device/entity is exposed to the outer world (providing the means
	to realize fixes/abstraction, alredy within zwave-core to keep
	home-assistant free from unneeded clutter.

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


