'''
OpenBlok | sub_process | ob_roi_frame.py

Cuts out the region of interest from the frame.
'''
import time
import numpy as np

from bloks.utils.bounding_areas import bounding_boxes
from modules import ob_storage


def capture_regions():
    '''
    Capture regions from frame.
    top_ul - top upper left (x,y)
    top_ll - top lower left (x,y)
    side_ul - side upper left (x,y)
    side_ll - side lower left (x,y)
    '''
    redis_db = ob_storage.RedisStorageManager()

    while True:
        frame_object = redis_db.get_frame("rotated", delete_frame=False)

        frame = frame_object['frame']
        metadata = frame_object['metadata']

        top_ul, top_ll, side_ul, side_ll = bounding_boxes()
        side_crop = frame[side_ul[1]:side_ll[1], side_ul[0]:side_ll[0]]
        top_crop = frame[top_ul[1]:top_ll[1], top_ul[0]:top_ll[0]]

        combined = np.concatenate((side_crop, top_crop), axis=1)

        metadata["roi"] = {
            "topView": {
                "upperLeft": [top_ul[0], top_ul[1]],
                "lowerRight": [top_ll[0], top_ll[1]]
            },
            "sideView": {
                "upperLeft": [side_ul[0], side_ul[1]],
                "lowerRight": [side_ll[0], side_ll[1]]
            },
            "shape": combined.shape,
        }

        # Save the frame to Redis
        redis_db.add_frame("roi", combined, metadata)

        # Sleep to maintain FPS
        time.sleep(1/30)
