# NOTE This code currently crashes on MacOS due to platform limitations.

import cv2
import threading
import queue
from object_ident import getObjects
import cv2
from control_pupper import send_control_signal
frame_height = 1280
frame_width = 720
thresh = 0.7  # Threshold to detect object
nms = 0.8
fps = 1000
delay_time = int(1000/fps)
frame_center = (frame_height//2, frame_width//2)
V_THRESH = 100
DELTA = 100
c = 600000
# Define camera capture thread


class CaptureThread(threading.Thread):
    def __init__(self, cap, frame_buffer):
        threading.Thread.__init__(self)
        self.cap = cap
        self.frame_buffer = frame_buffer
        self._stop_event = threading.Event()

    def run(self):
        while not self._stop_event.is_set():
            # Read frame from camera
            ret, frame = self.cap.read()

            # Add frame to buffer
            if ret:
                self.frame_buffer.put(frame)

    def stop(self):
        self._stop_event.set()

# Define frame processing thread


class ProcessThread(threading.Thread):
    def __init__(self, frame_buffer, processed_buffer):
        threading.Thread.__init__(self)
        self.frame_buffer = frame_buffer
        self.processed_buffer = processed_buffer
        self._stop_event = threading.Event()

    def run(self):
        while not self._stop_event.is_set():
            # Get frame from buffer
            frame = self.frame_buffer.get()

            # Process frame
            processed_frame = process_frame(frame)

            # Add processed frame to buffer
            self.processed_buffer.put(processed_frame)

    def stop(self):
        self._stop_event.set()

# Define frame display thread


class DisplayThread(threading.Thread):
    def __init__(self, processed_buffer):
        threading.Thread.__init__(self)
        self.processed_buffer = processed_buffer
        self._stop_event = threading.Event()

    def run(self):
        while not self._stop_event.is_set():
            # Get processed frame from buffer
            processed_frame = self.processed_buffer.get()

            # Display processed frame
            cv2.imshow("Processed Frame", processed_frame)

            # Wait for key press
            key = cv2.waitKey(delay_time)

            # Check for 'q' key press
            if key == ord('q'):
                break

    def stop(self):
        self._stop_event.set()


# Define frame processing function
def process_frame(frame):
    img = frame
    n_objects = 1
    result, objectInfo = getObjects(
        n_objects, img, thresh, nms, draw=False, frame_height=frame_height, frame_width=frame_width)
    # Check iff one objected is detected. If number of objects detected != 1 then continue in the loop
    if len(objectInfo) != 2:
        return img
    # print(objectInfo[1])
    # print(result)
    object_center = objectInfo[-1][0]
    A =  objectInfo[-1][1] 
    box = objectInfo[-1][2]
    # print(type(object_center[0]), type(object_center[1]))

    # Vector v denotes the magnitude and direction of Yaw control
    v = (object_center, (frame_center[0], object_center[1]))
    v_mod = frame_center[0] - object_center[0]

    # Only try to draw stuff that are well defined otherwise opencv will crash
    if v_mod < 0:
        print(f"direction is left to right, magnitude is {v_mod}, A = {A}")
    elif v_mod > 0:
        print(f"direction is right to left, magnitude is {v_mod}, A = {A}")
    else:
        print(f"No Yaw required")

    cv2.arrowedLine(img, object_center, (frame_center[0], object_center[1]), (255, 0, 0),
                    thickness=2, tipLength=0.5)
    # cv2.rectangle(img, box, color=(0, 255, 255), thickness=2)
    # cv2.circle(img, object_center, radius=V_THRESH,
    #                            color=(255, 255, 255), thickness=-1)
    # box2 = (frame_center[0], frame_center[1], DELTA, DELTA)
    
    # cv2.rectangle(img, box2, color=(0, 255, 255), thickness=2)
    send_control_signal(v_mod, A, keyboard = False)
    return img


# Create camera capture object, for the raspberry pi's usb camera, the rgb camera id is 2
cap = cv2.VideoCapture(2)
cap.set(3, frame_height)
cap.set(4, frame_width)
# Create frame buffers
frame_buffer = queue.Queue(maxsize=1)
processed_buffer = queue.Queue(maxsize=1)

# Create threads
capture_thread = CaptureThread(cap, frame_buffer)
process_thread = ProcessThread(frame_buffer, processed_buffer)
display_thread = DisplayThread(processed_buffer)

# Start threads
capture_thread.start()
process_thread.start()
display_thread.start()

# Wait for threads to finish
capture_thread.join()
process_thread.join()
display_thread.join()

# Release camera capture object and destroy windows
cap.release()
cv2.destroyAllWindows()
