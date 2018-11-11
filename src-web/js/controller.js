"use strict";
class Controller {
	constructor (net, io) {
		this.last_updated = Date.now();
		this.actions = [];
		this._net = null;

		this.io = io;
	}

	setup(net) {
		this._net = net;
		this._net.ctrl.push(this);

		gob.manager.get("/net/ctrl/actions", {},
			(ret) => ret.forEach(act => this.actions.push(act)));
		this.last_updated = Date.now();
	}

	teardown() {
		this.actions = [];
		this._net = null;
		this.last_updated = Date.now();
	}
}

