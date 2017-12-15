import json
import paho.mqtt.client as mqtt
from elasticsearch import Elasticsearch
from elasticsearch import helpers


class MyMQTTClass(mqtt.Client):

    def on_connect(self, mqttc, obj, flags, rc):
        self.es = Elasticsearch()
        print("rc: "+str(rc))

    def on_message(self, mqttc, obj, msg):
        # print(msg.topic+" "+str(msg.qos)+" "+str(json.loads(msg.payload)))
        try:
            helpers.bulk(self.es, [json.loads(msg.payload)])
        except:
            print('error')

    def on_subscribe(self, mqttc, obj, mid, granted_qos):
        print("Subscribed: "+str(mid)+" "+str(granted_qos))

    def on_log(self, mqttc, obj, level, string):
        print(string)

    def run(self):
        self.connect("test.mosquitto.org", 1883, 60)
        self.subscribe("aspm1188/data", 0)

        rc = 0
        while rc == 0:
            rc = self.loop()
        return rc



mqttc = MyMQTTClass()
rc = mqttc.run()

