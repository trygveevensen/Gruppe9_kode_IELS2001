import logging
import time
import random
import threading

from paho.mqtt import client as mqtt_client

BROKER = 'gruppe9.duckdns.org'
PORT = 1883
TOPICSUBSCRIBE = "liveSleepyTime/fromHome"
TOPICPUBLISH = "liveSleepyTime/fromRSi"
CLIENT_ID = f'PyTest {random.randint(1,10000)}'
USERNAME = 'gruppe9'
PASSWORD = 'cZgCp7cR-cZgCp7cR-cZgCp7cR'

FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60

FLAG_EXIT = False

sleeptimeFile = '/var/www/html/sleeptime.txt'
lastSleepTimeStamp = time.time()



def on_connect(client, userdata, flags, rc):
    if rc == 0 and client.is_connected():
        print("Connected to MQTT Broker!")
        client.subscribe(TOPICSUBSCRIBE)
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
    print(f'Received `{msg.payload.decode()}` from `{msg.topic}` topic')
    if msg.topic == TOPICSUBSCRIBE:
        arrival_time = time.time()
        global lastSleepTimeStamp
        lastSleepTimeStamp = arrival_time
        with open(sleeptimeFile, 'w') as f:
            f.write(f"{msg.payload.decode()},{arrival_time}")
        print(f"skrevet: {msg.payload.decode()},{arrival_time}")


def connect_mqtt():
    client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1, CLIENT_ID)
    client.username_pw_set(USERNAME, PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT, keepalive=120)
    client.on_disconnect = on_disconnect
    return client

def checkSleep(client):
    while True:
        try:
                time.sleep(1)
                global lastSleepTimeStamp
                with open(sleeptimeFile, 'r') as f:
                    innhold = f.read()

                currSleepTime = int(innhold.split(",")[0])
                currTimeStamp = float(innhold.split(",")[1])
                if currTimeStamp > lastSleepTimeStamp:
                    print(f"send, {currSleepTime}")
                    client.publish(TOPICPUBLISH,f"{currSleepTime}")
                    lastSleepTimeStamp = currTimeStamp
        except Exception as e:
            logging.error(f"Feil ved lesing av sleeptime.txt: {e}")

def run():
    logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s',level=logging.DEBUG)
    client = connect_mqtt()

    logic_thread = threading.Thread(target=checkSleep, args=(client,))
    logic_thread.daemon = True  # Optional: dies with main thread
    logic_thread.start()

    client.loop_forever()


if __name__ == "__main__":
    run()
