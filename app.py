import os
import random
from flask import Flask, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)

sound_base_dir = os.environ['HOME'] + '/soundPlayer/'

activation_time = timedelta(minutes=10)
last_sound_played_time = None
last_sound_played_name = None

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

# Functions for playing sounds
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
            return jsonify({'message': f'Random sound from "{directory}" played successfully'}), 200
        else:
            return jsonify({'error': f'No WAV files found in the "{directory}" directory'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Start Flask server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
