import os
import random
import time
import configparser
import paho.mqtt.client as mqtt
from datetime import datetime, timedelta

# Sound Player Configuration
sound_base_dir = os.environ['HOME'] + '/soundPlayer/'
activation_time = timedelta(minutes=10)
last_sound_played_time = None
last_sound_played_name = None

# MQTT Broker Settings
config = configparser.ConfigParser()
config.read('config.ini')

MQTT_BROKER = config['MQTT']['BROKER']
MQTT_PORT = int(config['MQTT']['PORT'])
MQTT_USERNAME = config['MQTT']['USERNAME']
MQTT_PASSWORD = config['MQTT']['PASSWORD']
MQTT_TOPIC = config['MQTT']['TOPIC']

# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    if rc == 0:
        client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    print(f"Message received: {msg.payload.decode()}")
    play_motion_alert_sound()

# Sound Playing Functions
def play_sound(sound_path):
    global last_sound_played_name, last_sound_played_time
    sound_path = os.path.join(sound_base_dir, sound_path)
    os.system(f'aplay {sound_path}')
    last_sound_played_name = sound_path
    last_sound_played_time = datetime.now()

def play_random_sound_from_directory(directory):
    try:
        sound_dir = os.path.join(sound_base_dir, directory)
        sound_files = [f for f in os.listdir(sound_dir) if f.endswith('.wav') and f != last_sound_played_name]
        
        if sound_files:
            random_sound = random.choice(sound_files)
            sound_path = os.path.join(sound_dir, random_sound)
            play_sound(sound_path)
            print(f"Played sound from {directory}: {sound_path}")
        else:
            print(f"No WAV files found in the '{directory}' directory")
    except Exception as e:
        print(f"Error: {str(e)}")

def play_motion_alert_sound():
    if last_sound_played_time is None or datetime.now() - last_sound_played_time > activation_time:
        play_random_sound_from_directory('funny')
    else:
        play_sound('alert.wav')

# Set up MQTT Client
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

# Connect and Start the Client
try:
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_forever()
except ConnectionRefusedError:
    print("The broker is not available or refused the connection.")