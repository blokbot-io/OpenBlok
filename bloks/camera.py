'''
Module | camera
Contains the configuration and controls for the camera.

- Usage -
Start the function continuous_capture() in a thread.
Use the function grab_frame() to get the last frame.
'''
#pylint: disable=C0301

import os
import time
from decimal import Decimal

import cv2
import config
import numpy as np

print("INFO | camera module loaded")

FPS = 30  # Frames per second


# ------------------------ Continuous Capture Thread ------------------------ #
def continuous_capture():
    '''
    Camera continues streaming frames. Only the last frame is saved when requested.
    Launch this function in a thread.
    '''
    def set_manual_exposure(dev_video_id, exposure_time):
        '''
        Manual exposure control
        '''
        commands = [
            ("v4l2-ctl --device /dev/video"+str(dev_video_id)+" -c exposure_auto=3"),
            ("v4l2-ctl --device /dev/video"+str(dev_video_id)+" -c exposure_auto=1"),
            ("v4l2-ctl --device /dev/video"+str(dev_video_id)+" -c exposure_absolute="+str(exposure_time))
        ]
        for command in commands:
            os.system(command)

    # Set Camera Parameters
    cap = cv2.VideoCapture(0)                   # Opens the USB camera stream
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)     # Set the width of the frame
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 2160)    # Set the height of the frame
    # cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 3)    # Set to 1 for manual or 3 for auto
    cap.set(cv2.CAP_PROP_FPS, FPS)              # Set frames per second
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)         # Set the buffer size to 1

    set_manual_exposure(0, 40)

    last_frame = None                           # Last frame taken
    while True:
        time_now = time.time()                  # Get the current time
        ret, last_frame = cap.read()                 # Read the frame
        print(f"Time to read frame: {time.time() - time_now}")

        if not ret or last_frame is None:
            print("WARNING | Can't receive frame (stream end?). Exiting ...")
            config.frame_queue = None

        if config.frame_queue is None:
            # Rotate the frame if needed
            if config.rotational_offset is not None:
                time_now = time.time()

                rotation_matrix = cv2.getRotationMatrix2D(
                    (config.rotational_offset[0], config.rotational_offset[1]),
                    config.rotational_offset[2], 1)
                frame = cv2.warpAffine(last_frame, rotation_matrix, (last_frame.shape[1], last_frame.shape[0]))

                print(f"Time to rotate: {time.time() - time_now}")

            config.frame_queue = [np.copy(last_frame), Decimal(time.time())]
            continue


# ---------------------------- Grab Frame Function --------------------------- #
def grab_frame():
    '''
    Call to get frame, returns the last taken frame.
    Returns: frame, time_stamp
    '''
    if config.requested_frame is None:
        config.frame_queue = None  # When set to none, the next frame will be saved.

    # Wait for the frame to be saved.
    while config.frame_queue is None:
        time.sleep(.001)

    config.requested_frame = np.copy(config.frame_queue[0], config.frame_queue[1])
    config.frame_queue = None  # When set to none, the next frame will be saved.

    return config.requested_frame[0], config.requested_frame[1]
