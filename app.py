import os
import random
from flask import Flask, jsonify
from datetime import datetime, timedelta, time as datetime_time
import time

app = Flask(__name__)

sound_base_dir = '/home/pi/soundPlayer/'

activation_threshold = 0.33

last_sound_played_time = None
last_sound_played_name = None

@app.route('/sound/funny', methods=['GET'])
def play_random_funny_sound():
    return play_random_sound_from_directory('funny')

@app.route('/sound/scary', methods=['GET'])
def play_random_scary_sound():
    if random.random() < activation_threshold:
        return play_random_sound_from_directory('scary')
    else:
        return jsonify({'message':'Scary sound ran, but not played'}), 200

@app.route('/sound/knocking', methods=['GET'])
def play_knocking_sound():
    if datetime.now().time() < datetime_time(17, 0, 0):  # Use the 'datetime_time' method
        return jsonify({'message': 'Its before the threshold time, no sound!'})
    time.sleep(10)
    global last_sound_played_time

    if last_sound_played_time is None:
        play_sound("scary/knock2.wav")
        last_sound_played_time = datetime.now()
        return jsonify({'success': 'Playing knocking!'})

    current_time = datetime.now()
    time_elapsed = current_time - last_sound_played_time

    if time_elapsed >= timedelta(minutes=10):
        play_sound("scary/knock2.wav")
        last_sound_played_time = current_time
        return jsonify({'success': 'Playing knocking!'})
    else:
        play_sound("scary/giggle.wav")
        return jsonify({'success': 'Playing giggle!'})

@app.route('/sound', methods=['GET'])
def play_random_sound_from_any_directory():
    all_sound_dirs = [d for d in os.listdir(sound_base_dir) if os.path.isdir(os.path.join(sound_base_dir, d))]
    if all_sound_dirs:
        random_directory = random.choice(all_sound_dirs)
        return play_random_sound_from_directory(random_directory)
    else:
        return jsonify({'error': 'No sound directories found'}), 404

def play_sound(sound_path):
    sound_path = os.path.join(sound_base_dir,sound_path)
    os.system(f'aplay {sound_path}')
    global last_sound_played_name
    last_sound_played_name = sound_path


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



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


