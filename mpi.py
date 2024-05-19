import os
import threading
import queue
import cv2  # OpenCV for image processing
from mpi4py import MPI  # MPI for distributed computing
import json

class WorkerThread(threading.Thread):
    def __init__(self, task_queue):
        threading.Thread.__init__(self)
        self.task_queue = task_queue
        self.comm = MPI.COMM_WORLD
        self.rank = self.comm.Get_rank()
        self.size = self.comm.Get_size()

    def run(self):
        while True:
            try:
                task = self.task_queue.get(timeout=1)
                if task is None:
                    break
                image, operation = task
                result = self.process_image(image, operation)
                self.send_result(image, operation, result)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error processing task: {e}")
                continue

    def process_image(self, image, operation):
        img = cv2.imread(image, cv2.IMREAD_COLOR)
        if operation == 'edge_detection':
            result = cv2.Canny(img, 100, 200)
        elif operation == 'color_inversion':
            result = cv2.bitwise_not(img)
        elif operation == 'grayscale':
            result = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        elif operation == 'blur':
            result = cv2.GaussianBlur(img, (5, 5), 0)
        elif operation == 'threshold':
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            _, result = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        elif operation == 'resize':
            result = cv2.resize(img, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_LINEAR)
        return result

    def send_result(self, image, operation, result):
        result_data = {
            'image': image,
            'operation': operation,
            'data': result
        }
        self.comm.send(result_data, dest=0)

def load_tasks(task_queue):
    with open('tasks.json', 'r') as file:
        tasks = json.load(file)
        for task in tasks:
            task_queue.put((task['image'], task['operation']))
    for _ in range(MPI.COMM_WORLD.Get_size() - 1):
        task_queue.put(None)

def distribute_tasks(task_queue):
    for _ in range(MPI.COMM_WORLD.Get_size() - 1):
        WorkerThread(task_queue).start()

def master_node(output_folder):
    result_list = []
    num_tasks = len(json.load(open('tasks.json')))  # Get the number of tasks
    for _ in range(num_tasks):
        result = MPI.COMM_WORLD.recv(source=MPI.ANY_SOURCE)
        result_list.append(result)
        image_path = result['image']
        image_name = os.path.basename(image_path).split('.')[0]  # Extract image name without extension
        operation = result['operation']
        processed_image_name = f"{image_name}_{operation}.jpg"
        cv2.imwrite(os.path.join(output_folder, processed_image_name), result['data'])
    return result_list

if __name__ == "__main__":
    task_queue = queue.Queue()
    output_folder = "processed_uploads"

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    if MPI.COMM_WORLD.Get_rank() == 0:
        load_tasks(task_queue)
        distribute_tasks(task_queue)
        master_node(output_folder)
    else:
        WorkerThread(task_queue).start()
