import os
import random
from flask import Flask, jsonify
from datetime import datetime, timedelta, time as datetime_time
import time
import configparser
import paho.mqtt.client as mqtt
import threading

app = Flask(__name__)

sound_base_dir = os.environ['HOME'] + '/soundPlayer/'

activation_threshold = 0.33
activation_time = timedelta(minutes=10)

last_sound_played_time = None
last_sound_played_name = None


# MQTT broker settings
config = configparser.ConfigParser()
config.read('config.ini')

MQTT_BROKER = config['MQTT']['BROKER']
MQTT_PORT = int(config['MQTT']['PORT'])
MQTT_USERNAME = config['MQTT']['USERNAME']
MQTT_PASSWORD = config['MQTT']['PASSWORD']
MQTT_TOPIC = config['MQTT']['TOPIC']

# MQTT callbacks
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    print(f"Message received: {msg.payload.decode()}")
    play_motion_alert_sound()
       

# Set up MQTT client
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)


# Flask Routes
@app.route('/sound/funny', methods=['GET'])
def play_random_funny_sound():
    return play_random_sound_from_directory('funny')

@app.route('/sound/scary', methods=['GET'])
def play_random_scary_sound():
    return play_random_sound_from_directory('scary')


@app.route('/sound', methods=['GET'])
def play_random_sound_from_any_directory():
    all_sound_dirs = [d for d in os.listdir(sound_base_dir) if os.path.isdir(os.path.join(sound_base_dir, d))]
    if all_sound_dirs:
        random_directory = random.choice(all_sound_dirs)
        return play_random_sound_from_directory(random_directory)
    else:
        return jsonify({'error': 'No sound directories found'}), 404







# Functions
def play_sound(sound_path):
    sound_path = os.path.join(sound_base_dir,sound_path)
    os.system(f'aplay {sound_path}')
    global last_sound_played_name
    last_sound_played_name = sound_path
    last_sound_played_time = time.Now()


def play_sound_from_path(sound_path):
    if os.path.exists():
        play_sound(sound_path)
    else:
        return jsonify({'error': f'File {sound_path} does not exist!'}), 404

def play_random_sound_from_directory(directory):
    try:
        sound_dir = os.path.join(sound_base_dir, directory)
        sound_files = [f for f in os.listdir(sound_dir) if f.endswith('.wav') and f != last_sound_played_name]
        
        if sound_files:
            random_sound = random.choice(sound_files)
            sound_path = os.path.join(sound_dir, random_sound)
            play_sound(sound_path)
            print(sound_path)
            return jsonify({'message': f'Random sound from "{directory}" played successfully'}), 200
        else:
            return jsonify({'error': f'No WAV files found in the "{directory}" directory'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def play_motion_alert_sound():
    # Play funny sound if last sound played was more than 10 minutes ago
    if last_sound_played_time is None or datetime.now() - last_sound_played_time > activation_time:
        play_random_sound_from_directory('funny')
    else: # play normal sound
        play_sound_from_path(os.path.join(sound_base_dir, 'alert.wav'))




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

