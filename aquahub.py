import time
import threading
import json
import paho.mqtt.client as mqtt
import temperature_probe

# --- Stub functions (to be implemented later) ---
def take_picture():
    print("📸 Taking a picture...")

def take_video():
    print("Taking a video...")

def feed():
    print("🐟 Dispensing food...")


# --- Load Config ---
with open("config.json") as f:
    config = json.load(f)

BROKER = config["broker"]
PORT = config["port"]
USERNAME = config.get("username")
PASSWORD = config.get("password")
TOPIC_TAKE_PICTURE = config["topics"]["take_picture"]
TOPIC_TAKE_VIDEO = config["topics"]["take_video"]
TOPIC_FEED = config["topics"]["feed"]
TOPIC_TEMPERATURE = config["topics"]["temperature"]
TEMP_INTERVAL = config.get("temperature_interval_seconds", 1800)

client = mqtt.Client("client_id","aquahub")

# --- MQTT Callbacks ---
def on_connect(client, userdata, flags, rc):
    print("Connected with result code", rc)
    client.subscribe([(TOPIC_TAKE_PICTURE, 0), (TOPIC_FEED, 0)])

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    print(f"Message on {msg.topic}: {payload}")

    if msg.topic == TOPIC_TAKE_PICTURE and payload == "1":
        take_picture()

    elif msg.topic == TOPIC_TAKE_VIDEO and payload == "1":
        take_picture()

    elif msg.topic == TOPIC_FEED and payload == "1":
        feed()


# --- Background Temperature Task ---
def temperature_task():
    while True:
        temp = temperature_probe.take_temperature()
        client.publish(TOPIC_TEMPERATURE, temp)
        print(f"Published temperature: {temp}")
        time.sleep(TEMP_INTERVAL)


# --- Main App ---
def main():
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set(USERNAME, PASSWORD)

    client.connect(BROKER, PORT, 60)

    # Start background thread for temperature publishing
    threading.Thread(target=temperature_task, daemon=True).start()

    # Loop forever handling MQTT
    client.loop_forever()


if __name__ == "__main__":
    main()

