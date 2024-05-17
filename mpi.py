import os
import threading
import queue
import cv2  # OpenCV for image processing
from mpi4py import MPI  # MPI for distributed computing

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
                self.send_result(result)
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

    def send_result(self, result):
        self.comm.send(result, dest=0)

def distribute_tasks(image_operations, task_queue):
    for i in range(MPI.COMM_WORLD.Get_size() - 1):
        WorkerThread(task_queue).start()
    for image, operation in image_operations:
        task_queue.put((image, operation))
    for i in range(MPI.COMM_WORLD.Get_size() - 1):
        task_queue.put(None)

def master_node(image_operations, output_folder):
    num_processes = MPI.COMM_WORLD.Get_size()
    result_list = []
    for i in range(len(image_operations)):
        result = MPI.COMM_WORLD.recv(source=MPI.ANY_SOURCE)
        result_list.append(result)
        idx = len(result_list) - 1
        image_name = os.path.basename(image_operations[idx][0])
        cv2.imwrite(os.path.join(output_folder, f"{image_name}_{image_operations[idx][1]}.jpg"), result)
    return result_list

if __name__ == "__main__":
    image_operations = [("images/image1.jpg", "edge_detection"),
                        ("images/image2.jpg", "color_inversion"),
                        ("images/image3.png", "grayscale"),
                        ("images/image1.jpg", "blur"),
                        ("images/image2.jpg", "threshold"),
                        ("images/image3.png", "resize")]

    task_queue = queue.Queue()
    output_folder = "output_images"

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    if MPI.COMM_WORLD.Get_rank() == 0:
        distribute_tasks(image_operations, task_queue)
        results = master_node(image_operations, output_folder)
    else:
        WorkerThread(task_queue).start()
