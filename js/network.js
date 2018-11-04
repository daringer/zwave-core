"use strict";

class Network {

	constructor (io) {
		this.last_updated = Date.now();
		this.actions = [];
		this.ctrl = [];
		this.io = io;
	}

	setup()  {
		gob.manager.get("/net/actions", {},
			(ret) => ret.data.forEach(act => this.actions.push(act)));
		this.last_updated = Date.now();
	}

	teardown() {
		if (this.ctrl.length > 0) {
			for(ctrl of this.ctrl)
				ctrl.teardown();
		} else
			this.io.warn("network teardown, but no controller was found");

		this.ctrl = [];
		this.actions = [];
		this.last_updated = Date.now();
	}
}

