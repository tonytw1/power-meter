from bluepy.btle import Scanner, DefaultDelegate, ScanEntry
import paho.mqtt.client as mqtt
import re
import binascii
import struct
import sys
import logging
logging.basicConfig(level=logging.INFO)

devices = ['f2:67:bf:fc:aa:98']
mqtt_host = "localhost"
mqtt_topic = 'abbottroad'

def log_mqtt_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

def log_mqtt_disconnect(client, userdata, rc):
    print("Disconnected with result code "+str(rc))

mqtt_client = mqtt.Client(client_id = "bluetooth-listener", clean_session = True)
mqtt_client.on_connect = log_mqtt_connect
mqtt_client.on_disconnect = log_mqtt_disconnect

logger = logging.getLogger(__name__)
mqtt_client.enable_logger(logger)

mqtt_client.connect(mqtt_host, 1883, 60)

# Allows the mqtt library to loop and reconnect while allowing th main thread to block in it's own loop
mqtt_client.loop_start()

joules_per_kilowatt_hour = 60 * 60 * 1000
ticks_per_kilowatt_hour = 800
joules_per_tick = joules_per_kilowatt_hour / ticks_per_kilowatt_hour

class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if (dev.addr in devices):
                short_addr = re.sub(':', '', dev.addr)
                data_items = dev.getScanData()
                manufacturer_specific_data_item = list(filter(lambda x: x[0] == ScanEntry.MANUFACTURER, data_items))
                if (len(manufacturer_specific_data_item) > 0):
                        value = manufacturer_specific_data_item[0][2]
                        count_hex = value[0:4]
                        count_bytes = binascii.unhexlify(count_hex)
                        count = struct.unpack('H', count_bytes)[0]

                        pulse_duration_hex = value[4:12]
                        pulse_duration_bytes = binascii.unhexlify(pulse_duration_hex)
                        pulse_duration = struct.unpack('I', pulse_duration_bytes)[0]

                        battery_voltage_hex = value[12:16]
                        battery_voltage_bytes = binascii.unhexlify(battery_voltage_hex)
                        battery_voltage = struct.unpack('H', battery_voltage_bytes)[0]

                        if (pulse_duration > 0):
                                ticks_per_second = float(1000) / pulse_duration
                                watts = int(round(ticks_per_second * joules_per_tick))
                                watts_message = short_addr + "watts:" + str(watts)
                                mqtt_client.publish(mqtt_topic, watts_message)

                        count_message = short_addr + "count:" + str(count)
                        mqtt_client.publish(mqtt_topic, count_message)

                        pulse_duration_message = short_addr + "pulseduration:" + str(pulse_duration)
                        mqtt_client.publish(mqtt_topic, pulse_duration_message)

                        battery_message = short_addr + "battery:" + str(battery_voltage)
                        mqtt_client.publish(mqtt_topic, battery_message)

scanner = Scanner().withDelegate(ScanDelegate())
scanner.start(passive=True)
while True:
    try:
        scanner.process()
    except Exception as e:
        print("Exception caught: ", e)
        raise(e)
