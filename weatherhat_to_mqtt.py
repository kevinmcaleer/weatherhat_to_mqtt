# Kevin McAleer 
# 18 February 2022
# This enables data from the Pimoroni WeatherHat to be sent to a local MQTT server

import weatherhat
import paho.mqtt.client as mqtt
from time import sleep
from datetime import datetime 

mqtt_server = '192.168.1.152' # Replace with the IP or URI of the MQTT server you use
client_id = "weatherhat"

update_frequency_in_seconds = 5

sensor = weatherhat.WeatherHAT()

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("$SYS/#")

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

client = mqtt.Client(client_id=client_id)
client.on_connect = on_connect
client.on_message = on_message
client.connect(host=mqtt_server)

payload = "{something:true}"
topic = 'weather'

import socket

# Wait until the network is and host name resolution is available:

def hostAvail(hostname):
    try:
        socket.gethostbyname(hostname)
        return True
    except socket.error:
        return False
    return False

while not hostAvail("weatherhatpi01"):
    print("Waiting for dbserver")
    sleep(2)

# Continue with code here...

while True:

    # update the sensor readings
    sensor.update(interval=1.0)
    
    # sleep for update frequency second 
    sleep(update_frequency_in_seconds)

    # build the payload
    now = datetime.now()
    payload = f'{{"datetime":{datetime.timestamp(now)}, "temperature":{sensor.temperature}, \
              "pressure":{sensor.pressure}, \
              "humidity":{sensor.humidity}, \
              "relative_humidity": {sensor.relative_humidity}, \
              "dewpoint":{sensor.dewpoint}, \
              "light":{sensor.lux}, \
              "wind_direction": {sensor.wind_direction}, \
              "wind_speed":{sensor.wind_speed}, \
              "rain": {sensor.rain}, \
              "rain_total":{sensor.rain_total} }}'
    client.publish(topic=topic, payload=payload, qos=0, retain=False)
    print(f"sending {payload} to server")