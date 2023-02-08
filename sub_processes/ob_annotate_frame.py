'''
OpenBlok | sub_process | ob_annotate_frame.py

Takes a predicted frame and annotates it with the predictions.
'''

import cv2

from bloks.utils import annotate, stats, bounding_boxes, crop_square
from modules import ob_storage

redis_db = ob_storage.RedisStorageManager()


def annotate(AruCo_corners, AruCo_ids, AruCo_center_x, mirror_offset, AruCo_px_per_inch):
    '''
    Take a rotated frame that has been predicted and annotate it.
    '''
    while True:
        predicted = redis_db.get_frame("predicted")
        predicted_frame = predicted['frame']
        predicted_side = list(predicted['side'])
        predicted_top = list(predicted['top'])
        predicted_preprocessed_shape = list(predicted['preprocessed_shape'])

        # Marker Layer
        cv2.aruco.drawDetectedMarkers(predicted_frame, AruCo_corners, AruCo_ids)

        # Split Line Layer
        cut_distance = int(AruCo_center_x +
                           (mirror_offset*AruCo_px_per_inch))
        cv2.line(predicted_frame, (cut_distance, 0),
                 (cut_distance, predicted_frame.shape[0]), (0, 0, 255), 2)

        # Bounding Box Layer
        bound_corners = bounding_boxes()
        predicted_frame = annotate.bounding_areas(predicted_frame, bound_corners)

        side = predicted_side
        top = predicted_top
        if 0 not in [side[0], side[1], top[0], top[1]] and top[0] > predicted_preprocessed_shape[1]//3:
            top[0] = top[0] - predicted_preprocessed_shape[1]//3
