import paho.mqtt.client as mqtt
import time
import logging
logging.basicConfig(level=logging.DEBUG)

mqtt_topic = 'test'

def log_mqtt_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

def log_mqtt_disconnect(client, userdata, rc):
    print("Disconnected with result code "+str(rc))

mqtt_client = mqtt.Client(client_id = "meh", clean_session = True)
mqtt_client.on_connect = log_mqtt_connect
mqtt_client.on_disconnect = log_mqtt_disconnect

logger = logging.getLogger(__name__)
mqtt_client.enable_logger(logger)

mqtt_client.connect("10.0.45.15", 32183, 60)

# Allows the mqtt library to loop and reconnect while allowing th main thread to block in it's own loop
mqtt_client.loop_start()

i = 0
while True:
	mqtt_client.publish(mqtt_topic, i)
	i = i + 1
	time.sleep(1)
