import json

from collections import namedtuple

from http import server
import paho.mqtt.client as mqtt

Subscription = namedtuple('Subscription', 'topic callback')

class crMQTT:

    def __init__(self,address,port):
        self.server_key = (address,port)
        self.mqtt_server = mqtt.Client()
        self.mqtt_server.on_connect = self.on_connect
        self.mqtt_server.on_message = self.on_message
        self.mqtt_server.connect(address,port,60)
        self.mqtt_server.loop_start()
        self.subscriptions = []

    def on_connect(self,client, userdata, flags, rc):
        self.register_subscriptions(self.subscriptions)

    def register_subscriptions(self,subs):
        for sub in subs:
            self.mqtt_server.subscribe(sub.topic)

    def match(self,tag,pattern):
        return True

    def on_message(self, client, userdata, message):
        m_raw = message.payload.decode("utf-8")
        m = json.loads(m_raw)
        m_topic = message.topic
        # print(f'Received <{m}> for topic <{m_topic}> from MQTT server')
        for sub in self.subscriptions:
            if self.match(m_topic,sub.topic):
                sub.callback(m_topic,m)

    def subscribe(self,topic,callback):
        subscription = Subscription(topic,callback)
        self.subscriptions.append(subscription)
        self.register_subscriptions(self.subscriptions)

    def publish(self,tag,message):
        self.mqtt_server.publish(tag,message)
