"use strict";


function CallbackQueue {
    // debug being set to true will lead to console outputs for many operations
    this.debug = true;

    // maps identifiers to callbacks
    this.callbacks = {};

    // keeps results to be handled
    this.queue = [];

    // time handle object
    this.timer = null;

    // register new callback with callback_id (cb_id) (overwrites, if cb_id already exists)
    // callbacks shall always be build for a single json-object argument 
    this.register = function(cb_id, cb) {
        this.callbacks[cb_id] = cb;
        if (this.debug)
            console.log("CallbackQueue::register cb_id: " + cb_id);
    };

    // enqueue new item (only if cb_id is known)
    this.push = function(cb_id, res_data) {
        if (!(cb_id in this.callbacks)) {
            console.error(cb_id + " not found in registered callback IDs, not queueing");
            return;
        }
        this.queue.push( [cb_id, res_data] );
        if (this.debug)
            console.log("CallbackQueue::push cb_id: " + cb_id + " with results: " + res_data);
    };

    // process next item in queue
    this.process = function() {
        if (this.queue.length == 0) {
            console.error("queue is empty, nothing to process");
            return;
        }
        var entry = this.queue.shift();
        var cb_id = entry[0];
        var res_data = entry[1];
        
        this.callbacks[cb_id](res_data);
        console.log("CallbackQueue::process cb_id: " + cb_id + " with results: " + res_data);
    };

    // de/activate automated, timer-based queue processing
    this.activate_worker = function(throttle_in_msecs=250) {
        this.timer = setInterval(this.worker.bind(this), throttle_in_msecs);
    };
    this.stop_worker = function() {
        clearInterval(this.timer);
    };
    // timer-worker function
    this.worker = function() {
        if (this.queue.length == 0)
            return;
        this.process();
    };
};

