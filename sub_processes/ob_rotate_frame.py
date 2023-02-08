'''
OpenBlok | sub_process | ob_rotate_frame.py
Ran as a subprocess to correct for the rotation of the camera.
'''

import cv2

from modules import ob_storage


redis_db = ob_storage.RedisStorageManager()


def rotation_correction(rotation_info):
    '''
    Grabs a frame from the queue and rotates it.
    '''
    print("Rotating frame", flush=True)
    while True:
        # Get frame from queue
        frame_object = redis_db.get_frame("raw")

        rotation_matrix = cv2.getRotationMatrix2D(
            (rotation_info['aruco_center_x'], rotation_info['aruco_center_y']),
            rotation_info['angle_offset'], 1)

        last_frame = cv2.warpAffine(
            frame_object['frame'], rotation_matrix,
            (frame_object['frame'].shape[1], frame_object['frame'].shape[0])
        )

        metadata = {'timestamp': frame_object['timestamp']}

        # Save the frame to Redis
        redis_db.add_frame("rotated", last_frame, metadata)
