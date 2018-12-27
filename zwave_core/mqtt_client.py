
import paho.mqtt.client as mqtt

class MyMQTTClient:
    def __init__(self, manager_host, manager_port):

        self.manager_port = manager_port
        self.manager_host = manager_host
        self.client = None

    def start(self, host=None, port=None):
        host = host or self.manager_host
        port = port or self.manager_port

        self.client = c = mqtt.Client()
        c.on_connect = self.on_connect
        c.on_message = self.on_message
        c.connect(host, port, 60)
        c.loop_start()

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()

    def on_connect(self, client, userdata, flags, rc):
        print (f"Connected to MQTT server result-code: {rc}")
        #client.subscribe("$SYS/#")
        #client.subscribe("zwave/#/set")

    def on_message(self, client, userdata, msg):
        print (f"[mqtt] topic: {msg.topic} || data: {str(msg.payload)}")

    def publish(self, topic, contents, retain=True, qos=0):
        """
        Publish `contents` to `topic`, descent/recurse, if sub-structure(s) found.
        Use key/index as topic postfix accordingly during descent...
        QoS: 0 => max. once ... 1 => min. once ... 2 => exactlly once
        """
        if isinstance(contents, dict):
            return [self.publish(f"{topic}/{key}", value, retain) for key, value in contents.items()]
        elif isinstance(contents, (tuple, list, set, frozenset)):
            return [self.publish(f"{topic}/{idx}", value, retain) for idx, value in enumerate(contents)]

        print (f"publishing: {topic}")
        return self.client.publish(topic, contents, qos=qos, retain=retain)

    def subscribe(self, topics):
        """Subscribe to `topics`, which has fmt: ["topic/123","bla/foo", [...]]"""
        if not isinstance(topics, (tuple, set, list, frozenset)):
            topics = [topics]

        for topic in topics:
            print (f"subscribing: {topic}")
            self.client.subscribe(topic)
            print (f"subscribed: {topic}")

