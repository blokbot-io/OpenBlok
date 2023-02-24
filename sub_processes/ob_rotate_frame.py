'''
OpenBlok | sub_process | ob_rotate_frame.py
Ran as a subprocess to correct for the rotation of the camera.
'''

import time

import cv2

from modules import ob_storage


def rotation_correction(rotation_info):
    '''
    Grabs a frame from the queue and rotates it.
    '''
    redis_db = ob_storage.RedisStorageManager()

    while True:
        frame_object = redis_db.get_frame("raw", delete_frame=False)    # Get frame from queue

        rotation_matrix = cv2.getRotationMatrix2D(
            (rotation_info['aruco_center_x'], rotation_info['aruco_center_y']),
            rotation_info['angle_offset'], 1)

        last_frame = cv2.warpAffine(
            frame_object['frame'], rotation_matrix,
            (frame_object['frame'].shape[1], frame_object['frame'].shape[0])
        )

        metadata = {
            'timestamp': frame_object['metadata']['timestamp'],
            'rotationCorrection': {
                "arucoCenterX": rotation_info['aruco_center_x'],
                "arucoCenterY": rotation_info['aruco_center_y'],
                "angleOffset": rotation_info['angle_offset']
            }
        }

        # Save the frame to Redis
        redis_db.add_frame("rotated", last_frame, metadata)

        # Sleep to maintain FPS
        time.sleep(1/30)
