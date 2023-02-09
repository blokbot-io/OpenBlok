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

        side = list(predicted['side'])
        top = list(predicted['top'])
        if 0 not in [side[0], side[1], top[0], top[1]] and top[0] > predicted_preprocessed_shape[1]//3:
            top[0] = top[0] - predicted_preprocessed_shape[1]//3

            # ----------------------------- Object Locations ----------------------------- #
            # Side View
            predicted_frame = annotate.mark_object_center(
                predicted_frame,
                (side[0]+bound_corners[2][0], side[1]+bound_corners[0][1]),
                (255, 0, 0)
            )

            side_crop = list(predicted['side_crop'])
            top_crop = list(predicted['top_crop'])

            predicted_frame = annotate.visualize_crop(
                predicted_frame,
                (side_crop[1][0]+bound_corners[2][0],
                 side_crop[1][1]+bound_corners[2][1]),
                (side_crop[2][0]+bound_corners[2][0],
                 side_crop[2][1]+bound_corners[2][1]),
                (255, 0, 0)
            )

            # Top View
            predicted_frame = annotate.mark_object_center(
                predicted_frame,
                (top[0]+bound_corners[0][0], top[1]+bound_corners[0][1])
            )

            predicted_frame = annotate.visualize_crop(
                predicted_frame,
                (top_crop[1][0]+bound_corners[0][0],
                 top_crop[1][1]+bound_corners[0][1]),
                (top_crop[2][0]+bound_corners[0][0],
                 top_crop[2][1]+bound_corners[0][1])
            )
