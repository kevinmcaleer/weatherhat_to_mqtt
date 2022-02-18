# Kevin McAleer 
# 18 February 2022
# This enables data from the Pimoroni WeatherHat to be sent to a local MQTT server

import weatherhat

import time
from umqttsimple import MQTTClient
import ubinascii
import machine
import micropython
import network
import esp
esp.osdebug(None)
import gc
gc.collect()
import dht

# Replease the ssid text with the network name for your local Wifi connection
# replace the password text with the WiFi password
# replace the mqtt_server text with the mqtt server IP or url
# replace the topic_sub with the topic you want to subscribe to 
# replace the topic_pub with the topic you want to publish to

ssid = 'insert your SID here'
password = 'your password'
mqtt_server = 'your MQTT IP' # Replace with the IP or URI of the MQTT server you use
client_id = ubinascii.hexlify(machine.unique_id())
topic_sub = b'flag' # This is the topic you want to subscribe to
topic_pub = b'weatherbot' # This is the topic you want to publish to
servo_pin = machine.PWM(machine.Pin(2))
print(servo_pin.freq())
print("setting servo to 50hz")
servo_pin.freq(50)
print(servo_pin.freq())
dht22 = dht.DHT22(machine.Pin(4))

last_message = 0
message_interval = 5
counter = 0

station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
    pass

print('Connection successful')
print(station.ifconfig())

def sub_cb(topic, msg):
    print((topic, msg))
    if topic == b'notification' and msg == b'received':
        print('ESP received hello message')
    if topic == b'flag':
        print("move flag",msg)
        move_flag(msg)
        

def connect_and_subscribe():
    global client_id, mqtt_server, topic_sub
    client = MQTTClient(client_id, mqtt_server)
    client.set_callback(sub_cb)
    client.connect()
    client.subscribe(topic_sub)
    print('Connected to %s MQTT broker, subscribed to %s topic' % (mqtt_server, topic_sub))
    return client

def restart_reconnect():
    print('Failed toconnect to MQTT broker, Reconnecting...')
    time.sleep(10)
    machine.reset()
    
def map(x, in_min, in_max, out_min, out_max):
    return int((x-in_min) * (out_max-out_min) / (in_max - in_min) + out_min)

def move_flag(angle):
    pulse = map(int(angle), in_min=0 , in_max=180,out_min=40, out_max=115)
    print("Angle:", angle, "Pulse:", pulse)
    
    servo_pin.duty(pulse)
    time.sleep(1)

def temp_indicator(temp):
    """ moves the indicator angle based on the temp coming in """
    angle = map(int(temp), in_min=0, in_max=50, out_min=180, out_max=0)
    print("temp is:", temp ,"angle is:",angle)
    move_flag(angle)

print("waking up")
for n in range(3):
    temp_indicator(1)
    time.sleep(0.25)
    temp_indicator(50)
    time.sleep(0.25)
print("woke up")

try:
    client = connect_and_subscribe()
except OSError as e:
    restart_and_reconnect()
    
while True:
    try:
        client.check_msg()
        print("measuring Temp")
        dht22.measure()
        print("setting angle")
        temp_indicator(dht22.temperature())
        msg = str(dht22.temperature())

    except OSError as e:
        restart_and_reconnect()