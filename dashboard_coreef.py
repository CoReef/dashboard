import json
import time

import crMQTT
# Address of the MQTT server
mqtt_address = '10.42.1.102'
mqtt_port = 1884
mqtt = crMQTT.crMQTT(mqtt_address,mqtt_port)

def on_message(tag,message):
    print(tag)
    print(message)

def main():
    mqtt.subscribe('#',on_message)
    while True:
        time.sleep(60)

if __name__ == '__main__':
    main()
