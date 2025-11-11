from flask import Flask, render_template, request, jsonify, Response
import subprocess
import os
import signal
import cv2

app = Flask(__name__)

current_process = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/capture', methods=['POST'])
def capture():
    global current_process

    data = request.json
    person_name = data.get('name', '').strip()

    if not person_name:
        return jsonify({'success': False, 'message': 'Person name is required'})

    try:
        with open('imagecapture.py', 'r') as file:
            content = file.read()

        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'sub_data' in line and '=' in line:
                lines[i] = f"sub_data = '{person_name}'"
                break

        updated_content = '\n'.join(lines)
        with open('imagecapture.py', 'w') as file:
            file.write(updated_content)

        if current_process:
            try:
                current_process.terminate()
                current_process.wait(timeout=2)
            except:
                pass

        current_process = subprocess.Popen(['python', 'imagecapture.py'])

        return jsonify({'success': True, 'message': f'Image capture started for {person_name}'})

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/recognize', methods=['POST'])
def recognize():
    global current_process

    try:
        if current_process:
            try:
                current_process.terminate()
                current_process.wait(timeout=2)
            except:
                pass

        current_process = subprocess.Popen(['python', 'facereco.py'])

        return jsonify({'success': True, 'message': 'Face recognition started'})

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/stop', methods=['POST'])
def stop():
    global current_process

    try:
        if current_process:
            current_process.terminate()
            current_process.wait(timeout=2)
            current_process = None
            return jsonify({'success': True, 'message': 'Process stopped'})
        else:
            return jsonify({'success': False, 'message': 'No process running'})

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/get_persons', methods=['GET'])
def get_persons():
    try:
        datasets = 'images'
        if os.path.exists(datasets):
            persons = [d for d in os.listdir(datasets) if os.path.isdir(os.path.join(datasets, d))]
            return jsonify({'success': True, 'persons': persons})
        else:
            return jsonify({'success': True, 'persons': []})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
