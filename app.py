import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import glob
from flask_cors import CORS
import logging
import time
from calculate_measurements import calculate_body_measurements
from calculate_measurements import process_image
from human_model import create_model, get_model, download_glb
from imgur_adress import upload_to_imgur


app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('userdata.html')


# Ordner zum Speichern der hochgeladenen Dateien
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#Globale Variablen
known_height = None
image_path = None


@app.route('/userdata', methods=['POST'])
def upload_file():
    global known_height, image_path

    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    user_size = request.form.get('size')

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not user_size:
        return jsonify({'error': 'No size provided'}), 400

    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    # Speichern der Nutzergrößen
    user_data = {
        'filename': filename,
        'size': user_size
    }

    # Speichern in einer Datei
    with open(os.path.join(app.config['UPLOAD_FOLDER'], f"{filename}.txt"), 'w') as f:
        f.write(f"{user_size}")

    # Suche nach einer Bilddatei im Ordner uploads
    image_files = glob.glob(os.path.join(app.config['UPLOAD_FOLDER'], '*.*'))
    image_files = [f for f in image_files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]

    if not image_files:
        return jsonify({"error": "No image file found in the uploads folder"}), 400

    # Nimmt das erste gefundene Bild
    image_path = image_files[0]

    # Suche nach der Textdatei im Ordner uploads
    text_files = glob.glob(os.path.join(app.config['UPLOAD_FOLDER'], '*.txt'))

    if not text_files:
        return jsonify({"error": "No text file found in the uploads folder"}), 400

    # Nimmt die erste gefundene Textdatei
    text_file_path = text_files[0]

    try:
        with open(text_file_path, 'r') as file:
            known_height = float(file.read().strip())
    except Exception as e:
        return jsonify({"error": f"Error reading height from text file: {str(e)}"}), 500

    return jsonify({'message': 'File and size successfully uploaded!'}), 200


@app.route('/measurements', methods=['GET'])
def measurements():
    global known_height, image_path

    if not known_height or not image_path:
        return jsonify({"error": "Data not set"}), 400

    try:
        landmark_data = process_image(image_path)
    except Exception as e:
        return jsonify({"error": f"Error processing image: {str(e)}"}), 500

    try:
        body_measurements = calculate_body_measurements(landmark_data, known_height)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"measurements": body_measurements}), 200


@app.route('/humanmodel', methods=['GET'])
def humanmodel():
    #image_path = "uploads/test_thomas.JPG"
    #model_id = "0190c078-e20c-7b8b-868a-0f0396c0c718"

    global image_path

    # Imgur API
    public_url = upload_to_imgur(image_path)

    #Calling the Meshy API for 3D Model
    model_id = create_model(public_url)
    time.sleep(90)
    model = get_model(model_id)

    download_glb(model)

    return send_from_directory('standard', 'model.glb'), 200


@app.route('/list_models', methods=['GET'])
def list_models():
    models_dir = 'glb'
    models = [f for f in os.listdir(models_dir) if f.endswith('.glb')]
    return jsonify(models), 200


@app.route('/get_model/<filename>', methods=['GET'])
def get_model(filename):
    models_dir = 'glb'
    if filename in os.listdir(models_dir):
        return send_from_directory(models_dir, filename), 200
    else:
        return jsonify({"error": "File not found"}), 404


@app.route('/get_thumbnail/<filename>', methods=['GET'])
def get_thumbnail(filename):
    thumbnails_dir = 'glb'
    if filename in os.listdir(thumbnails_dir):
        return send_from_directory(thumbnails_dir, filename), 200
    else:
        return jsonify({"error": "File not found"}), 404


if __name__ == '__main__':
    app.run()
