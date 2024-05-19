# Image Processing Web Application

This web application allows users to upload images and perform various processing tasks on them. The application is built using Flask and leverages multi-threading for handling concurrent requests and MPI (Message Passing Interface) for parallel processing of image tasks.

## Features

- Upload multiple images and specify processing operations.
- Background processing of images using MPI for parallel execution.
- Retrieve URLs of processed images.

## Flask Application (Multi-threading)

The Flask app handles web requests and processes them using multi-threading to ensure responsiveness. When a file upload request is received, a background thread is started to handle MPI invocation, allowing the main server to continue processing other requests.

```python
threading.Thread(target=invoke_mpi).start()
```

## MPI Script (Multiple Processes)

The `invoke_mpi()` function in the Flask app calls an external script (mpi.py) using MPI. The script is executed with multiple processes to perform parallel image processing tasks efficiently.

MPI Command:

```python
subprocess.run(['mpiexec', '-n', '2', 'python3', 'mpi.py'])
```

- `-n 2`: Specifies the number of processes (2 in this case).
- `mpi.py`: The script to be executed in parallel.

## Requirements

- Python 3.x
- Flask
- MPI (Message Passing Interface) implementation (e.g., Open MPI)
- Necessary Python packages (flask, os, subprocess, threading, json)

## Installation

1. clone the repository:
   ```bash
   git clone https://github.com/abozaid01/Distributed-Image-Processing-on-AWS.git
   cd Distributed-Image-Processing-on-AWS/
   ```
2. Create a virtual environment and install dependencies (optional):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install flask
   ```
3. Install MPI:
   ```bash
   sudo apt-get update
   sudo apt-get install -y mpich
   ```

## Usage

1. Start the Flask application:

   ```bash
   python3 server.py
   ```

2. Access the application:
   Open your web browser and go to `http://127.0.0.1:5000/`.

3. Upload images and specify operations:

   - Use the web interface to upload images and specify the desired operations for each image.
   - The application will save the uploaded files and queue the processing tasks.

4. Retrieve processed images:

   - The application will process the images in the background using MPI.
   - You can retrieve the processed images from the specified URLs provided after uploading.

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

## License

This project is licensed under the [MIT](https://choosealicense.com/licenses/mit/) License. See the LICENSE file for details.
