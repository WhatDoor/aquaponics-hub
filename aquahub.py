import time
import threading
import json
import paho.mqtt.client as mqtt
import temperature_probe
from gpiozero import Servo
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder, Quality

picam2 = Picamera2()
still_config = picam2.create_still_configuration()
video_config = picam2.create_video_configuration(main={"size": (1640, 1232)})

def take_picture():
    print("📸 Taking a picture...")
    picam2.configure(still_config)
    picam2.start()
    picam2.capture_file("picture.png")
    picam2.stop()
    print("Picture taken!")

def take_video():
    print("📸 Taking a video...")
    picam2.configure(video_config)
    encoder = H264Encoder()
    picam2.start_recording(encoder, 'video.h264', quality=Quality.HIGH)
    time.sleep(10)
    picam2.stop_recording()

    print("Video taken!")

def feed(feedCount):
    print("🐟 Dispensing food..." + str(feedCount) + " feeds.") 

    servo = Servo(17)
    time.sleep(0.5)
    
    for i in range(feedCount):
        print("Feeding... " + str(i+1) + "/" + str(feedCount))
        # Adjust pulse widths for your servo's range
        servo.min()  # One end (~0°)
        time.sleep(0.3)
        servo.max()  # One end (~0°)
        time.sleep(2)

    print("Feed dispense complete!") 


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
    client.subscribe([(TOPIC_TAKE_PICTURE, 2), (TOPIC_FEED, 2), (TOPIC_TAKE_VIDEO, 2)])

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    print(f"Message on {msg.topic}: {payload}")

    if msg.topic == TOPIC_TAKE_PICTURE and payload == "1":
        take_picture()

    elif msg.topic == TOPIC_TAKE_VIDEO and payload == "1":
        take_video()

    elif msg.topic == TOPIC_FEED:
        feedCount = int(payload)
        feed(feedCount)


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

