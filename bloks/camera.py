'''
Module | camera
Contains the configuration and controls for the camera.

- Usage -
Start the function continuous_capture() in a thread.
Use the function grab_frame() to get the last frame.
'''
#pylint: disable=C0301

import time
# from decimal import Decimal

import cv2

from modules import ob_storage

print("INFO | camera module loaded")

FPS = 30  # Frames per second


save_local = ob_storage.LocalStorageManager()
redis_db = ob_storage.RedisStorageManager()


# ------------------------ Continuous Capture Thread ------------------------ #
def continuous_capture():
    '''
    Camera continues streaming frames. Only the last frame is saved when requested.
    Launch this function in a thread.
    '''
    # Set Camera Parameters
    cap = cv2.VideoCapture(0)                   # Opens the USB camera stream
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)     # Set the width of the frame
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 2160)    # Set the height of the frame
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 5)         # Set the buffer size to 1
    cap.set(cv2.CAP_PROP_FPS, FPS)              # Set frames per second
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))

    frame_count = 0                             # Frame counter
    last_frame = None                           # Last frame taken
    while True:
        ret, last_frame = cap.read()                 # Read the frame

        if not ret or last_frame is None:
            print("WARNING | Can't receive frame (stream end?). Exiting ...")
            continue

        # Save the frame to the local storage
        save_local.add_image(last_frame, frame_count)
        frame_count += 1

        metadata = {'timestamp': time.time()}

        # Save the frame to Redis
        redis_db.add_frame("raw", last_frame, metadata)
