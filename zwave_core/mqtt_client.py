
from hbmqtt.client import MQTTClient, ClientException
from hbmqtt.mqtt.constants import QOS_1, QOS_2


class MyMQTTClient:
    client_mqtt_config = {
        "keep_alive": 10,
        "ping_delay": 1,
        "default_qos": 0,
        "default_retain": False,
        "auto_reconnect": True,
        "reconnect_max_interval": 5,
        "reconnect_retries": 10,
        #'topics': {
        #    '/test': { 'qos': 1 },
        #    '/some_topic': { 'qos': 2, 'retain': True }
        #}
    }

    def __init__(self, manager_host, manager_port, base_topic="zwave",
                 raw_topic="raw", export_topic="all"):

        self.manager_port = manager_port
        self.manager_host = manager_host
        self.client = MQTTClient(config=self.client_mqtt_config)
        self.client.connect(f"mqtt://{manager_host}:{manager_port}/").close()

    def publish(self, topic, contents):
        if isinstance(contents, dict):
            return list(map(lambda x: x.close(), [self.publish(f"{topic}/{key}", value) for key, value in contents.items()]))
        elif isinstance(contents, (tuple, list, set, frozenset)):
            return list(map(lambda x: x.close(), [self.publish(f"{topic}/{idx}", value) for idx, value in contents]))
        else:
            return self.client.publish(topic, contents)

    def subscribe(self, topics):
        """
        Subscribe to `topics`, which has fmt:
            [["topic/123", QOS_1],["bla/foo", QOS_1],[...]]
        """
        self.client.subscribe(topics)

    def recv_topic(self, timeout=0):
        """
        Receives updates from subscribed topics. timeout=0 blocking forever, >0 raises Exception
        """
        out = None, None
        try:
            msg = self.client.deliver_message(timeout=timeout).close()
            p = msg.publish_packet
            topic, data = p.variable_header.topic_name, p.payload.data
            out = topic, data
        except ClientException as e:
            print (f"timeout or error: {e}")

        return out

    def destroy(self):
        self.client.disconnect().close()


