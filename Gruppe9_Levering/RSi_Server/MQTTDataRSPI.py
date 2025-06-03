import logging
import time
import subprocess
import random

from paho.mqtt import client as mqtt_client

BROKER = 'localhost'
PORT = 1883
CLIENT_ID = f'PyTest {random.randint(1,10000)}'
USERNAME = 'testEH'
PASSWORD = '123321'

FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60

FLAG_EXIT = False

p = subprocess.Popen(["/home/ehkr7bk1/Documents/MQTTENV/bin/python", "/home/ehkr7bk1/Documents/MQTTDataLagreTest/graf.py"])

def on_connect(client, userdata, flags, rc):
    if rc == 0 and client.is_connected():
        print("Connected to MQTT Broker!")
        client.subscribe("data")
        client.subscribe("sleepRequest")
    else:
        print(f'Failed to connect, return code {rc}')


def on_disconnect(client, userdata, rc):
    logging.info("Disconnected with result code: %s", rc)
    reconnect_count, reconnect_delay = 0, FIRST_RECONNECT_DELAY
    while reconnect_count < MAX_RECONNECT_COUNT:
        logging.info("Reconnecting in %d seconds...", reconnect_delay)
        time.sleep(reconnect_delay)

        try:
            client.reconnect()
            logging.info("Reconnected successfully!")
            return
        except Exception as err:
            logging.error("%s. Reconnect failed. Retrying...", err)

        reconnect_delay *= RECONNECT_RATE
        reconnect_delay = min(reconnect_delay, MAX_RECONNECT_DELAY)
        reconnect_count += 1
    logging.info("Reconnect failed after %s attempts. Exiting...", reconnect_count)
    global FLAG_EXIT
    FLAG_EXIT = True


def on_message(client, userdata, msg):
    logging.info(f"Topic: {msg.topic} || MSG: {msg.payload.decode()}")
    global p
    arrival_time = time.time()
    if msg.topic == "data":
        f = open("/var/www/html/data.txt", "a")
        f.write(f"{arrival_time},{msg.payload.decode()}\n")
        f.close()
        finnished = not (p.poll() is None)
        if finnished:
            p = subprocess.Popen(["/home/ehkr7bk1/Documents/MQTTENV/bin/python", "/home/ehkr7bk1/Documents/MQTTDataLagreTest/graf.py"])
    if msg.topic == "sleepRequest":
        g = open("/var/www/html/sleeptime.txt")
        payload = g.read()
        logging.info(f"payload: {payload}")
        client.publish("sleepyTime",f"{payload}")
        g.close()

def connect_mqtt():
    client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1,CLIENT_ID)
    client.username_pw_set(USERNAME, PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT, keepalive=120)
    client.on_disconnect = on_disconnect
    return client


def run():
    logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s',
                        level=logging.DEBUG)
    client = connect_mqtt()
    client.loop_forever()


if __name__ == '__main__':
    run()
