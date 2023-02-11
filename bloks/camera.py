'''
Module | camera
Contains the configuration and controls for the camera.

- Usage -
Start the function continuous_capture() in a thread.
'''

import time

import cv2

from modules import ob_storage

print("INFO | camera module loaded")

FPS = 30  # Frames per second


def continuous_capture():
    '''
    Camera continues streaming frames. Only the last frame is saved when requested.
    Launch this function as a thread.
    '''
    save_local = ob_storage.LocalStorageManager()
    redis_db = ob_storage.RedisStorageManager()

    # ----------------------------- Camera Properties ---------------------------- #
    cap = cv2.VideoCapture(0)                   # Opens the USB camera stream
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)     # Set the width of the frame
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 2160)    # Set the height of the frame
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)         # Set the buffer size to 1
    cap.set(cv2.CAP_PROP_FPS, FPS)              # Set frames per second
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))

    frame_count = 0                             # Frame counter
    while True:
        status, new_frame = cap.read()                 # Read the frame

        if not status:
            print("WARNING | Can't receive frame (stream end?). Exiting ...")
            continue

        # Save the frame to the local storage
        save_local.add_image(new_frame, frame_count)

        # Save the frame to Redis
        redis_db.add_frame("raw", new_frame, {'timestamp': time.time()})

        frame_count += 1

        # Sleep to maintain FPS
        time.sleep(1 / FPS)
