from flask import Flask, request, jsonify, render_template, send_from_directory
import os
import subprocess
import threading
import json

app = Flask(__name__)


# Folders for saving uploaded and processed images
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed_uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

TASK_FILE = 'tasks.json'

@app.route('/')
def index():
    return render_template('index.html')

def save_file(file, folder):
    """
    Save the uploaded file to the specified folder.
    """
    file_path = os.path.join(folder, file.filename)
    file.save(file_path)
    return file_path

def write_tasks_to_file(tasks):
    """
    Write the list of tasks to the tasks.json file.
    """
    with open(TASK_FILE, 'w') as file:
        json.dump(tasks, file)

def delete_past_files(folder):
    """
    Delete past files in the specified folder.
    """
    for file_name in os.listdir(folder):
        file_path = os.path.join(folder, file_name)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Error deleting file: {e}")

def invoke_mpi():
    """
    Function to invoke the MPI script to process tasks in the queue.
    """
    try:
        subprocess.run(['mpiexec', '-n', '2', 'python3', 'mpi.py'])
    except Exception as e:
        print(f"Error occurred during MPI processing: {e}")


@app.route('/upload', methods=['POST'])
def upload_files():
    """
    Route to handle file uploads. Queues the image processing tasks.
    """
    if 'files' not in request.files or 'operations' not in request.form:
        return jsonify({'error': 'No file or operation part in the request'}), 400
    
    # Delete past files in the upload and processed folders
    delete_past_files(UPLOAD_FOLDER)
    delete_past_files(PROCESSED_FOLDER)

    files = request.files.getlist('files')
    operations = request.form.getlist('operations')

    if not files or any(file.filename == '' for file in files):
        return jsonify({'error': 'No files selected for uploading'}), 400

    # Save the uploaded files and queue the tasks
    tasks = []
    for file, operation in zip(files, operations):
        file_path = save_file(file, UPLOAD_FOLDER)
        tasks.append({'image': file_path, 'operation': operation})
    
    # Write tasks to tasks.json file
    write_tasks_to_file(tasks)

    # Start MPI processing in a background thread
    threading.Thread(target=invoke_mpi).start()

    # Generate processed file paths
    processed_files = [os.path.join(PROCESSED_FOLDER, f"{file.filename.split('.')[0]}_{operation}.jpg") for file, operation in zip(files, operations)]

    return jsonify({'message': 'Files uploaded and processing started successfully', 'processed_files': processed_files}), 200

@app.route('/processed_uploads/<filename>')
def processed_file(filename):
    """
    Route to serve the processed image files.
    """
    return send_from_directory(PROCESSED_FOLDER, filename)


@app.route('/get_processed_images')
def get_processed_images():
    """
    Route to fetch the URLs of processed images.
    """
    processed_files = [f for f in os.listdir(PROCESSED_FOLDER) if f.endswith('.jpg')]
    processed_files_urls = [f'/processed_uploads/{filename}' for filename in processed_files]
    return jsonify({'processed_files': processed_files_urls})

if __name__ == '__main__':
    app.run(debug=True)
