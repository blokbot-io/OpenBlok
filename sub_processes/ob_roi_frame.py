'''
OpenBlok | sub_process | ob_roi_frame.py

Cuts out the region of interest from the frame.
'''
import time
import numpy as np

import cv2

from bloks.utils.bounding_areas import bounding_boxes
from modules import ob_storage, ob_trilateration


def combined_roi_views(image, side_rect, top_rect):
    '''
    Compensates for missed mixes to ensure:
    - top view as a h:w ratio of 1:1
    - side view h is equal to top view h
    - side view as a h:w ratio of 1:2
    '''
    (side_tl, side_tr, side_br, side_bl) = side_rect
    (top_tl, top_tr, top_br, top_bl) = top_rect
    # Calculate the max height for the side and top views then get the average.

    # Side Max Height
    side_heightA = np.sqrt(((side_tr[0] - side_br[0]) ** 2) + ((side_tr[1] - side_br[1]) ** 2))
    side_heightB = np.sqrt(((side_tl[0] - side_bl[0]) ** 2) + ((side_tl[1] - side_bl[1]) ** 2))
    side_maxHeight = max(int(side_heightA), int(side_heightB))

    # Top Max Height
    top_heightA = np.sqrt(((top_tr[0] - top_br[0]) ** 2) + ((top_tr[1] - top_br[1]) ** 2))
    top_heightB = np.sqrt(((top_tl[0] - top_bl[0]) ** 2) + ((top_tl[1] - top_bl[1]) ** 2))
    top_maxHeight = max(int(top_heightA), int(top_heightB))

    average_height = int((side_maxHeight + top_maxHeight) / 2)

    # Subtract 1 if average_height is not divisible by 2
    if average_height % 2 != 0:
        average_height -= 1

    side_dst = np.array([
        [0, 0],
        [average_height/2 - 1, 0],
        [average_height/2 - 1, average_height - 1],
        [0, average_height - 1]], dtype="float32")

    top_dst = np.array([
        [0, 0],
        [average_height - 1, 0],
        [average_height - 1, average_height - 1],
        [0, average_height - 1]], dtype="float32")

    side_M = cv2.getPerspectiveTransform(side_rect, side_dst)
    top_M = cv2.getPerspectiveTransform(top_rect, top_dst)

    side_warped = cv2.warpPerspective(image, side_M, (int(average_height/2), average_height))
    top_warped = cv2.warpPerspective(image, top_M, (average_height, average_height))

    return np.concatenate((side_warped, top_warped), axis=1)


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
        try:
            frame_object = redis_db.get_frame("raw", delete_frame=False)

            frame = frame_object['frame']
            metadata = frame_object['metadata']

            # top_ul, top_ll, side_ul, side_ll = bounding_boxes()
            # side_crop = frame[side_ul[1]:side_ll[1], side_ul[0]:side_ll[0]]
            # top_crop = frame[top_ul[1]:top_ll[1], top_ul[0]:top_ll[0]]

            # combined = np.concatenate((side_crop, top_crop), axis=1)

            view_points = ob_trilateration.calculated_roi_corners(frame)

            side_rect = np.array([
                view_points["svtl"][0:2],
                view_points["svtr"][0:2],
                view_points["svbr"][0:2],
                view_points["svbl"][0:2]], dtype=np.float32)

            top_rect = np.array([
                view_points["tvtl"][0:2],
                view_points["tvtr"][0:2],
                view_points["tvbr"][0:2],
                view_points["tvbl"][0:2]], dtype=np.float32)

            combined = combined_roi_views(frame, side_rect, top_rect)

            metadata["roi"] = {
                "topView": {
                    "upperLeft": [int(view_points["tvtl"][0]), int(view_points["tvtl"][1])],
                    "lowerRight": [int(view_points["tvbr"][0]), int(view_points["tvbr"][1])]
                },
                "sideView": {
                    "upperLeft": [int(view_points["svtl"][0]), int(view_points["svtl"][1])],
                    "lowerRight": [int(view_points["svbr"][0]), int(view_points["svbr"][1])]
                },
                "shape": combined.shape,
            }

            # Save the frame to Redis
            redis_db.add_frame("roi", combined, metadata)

            # Sleep to maintain FPS
            time.sleep(1/30)
        except Exception as e:
            print(e)
