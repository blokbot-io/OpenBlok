'''
OpenBlok | sub_process | ob_annotate_frame.py

Takes a predicted frame and annotates it with the predictions.
'''

import json

import cv2
import config

from bloks.utils import annotate, stats, bounding_boxes
from modules import ob_storage

redis_db = ob_storage.RedisStorageManager()


def annotations(AruCo_corners, AruCo_ids, AruCo_center_x, mirror_offset, AruCo_px_per_inch):
    '''
    Take a rotated frame that has been predicted and annotate it.
    '''

    session_stats = stats.Stats()

    while True:
        predicted = redis_db.get_frame("predicted")
        predicted_frame = predicted['frame']

        predicted_preprocessed_shape = predicted_frame.shape

        print(predicted_preprocessed_shape)

        session_stats.add_frame_time(predicted['timestamp'])    # Add frame time to stats

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

        print(type(predicted['side']))
        print(predicted['top'])

        side = json.loads(predicted['side'])
        top = json.loads(predicted['top'])

        print(side)
        print(top)

        # side = [float(i) for i in side]
        # top = [float(i) for i in top]

        if 0 not in [side[0], side[1], top[0], top[1]] and top[0] > predicted_preprocessed_shape[1]//3:
            top[0] = top[0] - predicted_preprocessed_shape[1]//3

            # ----------------------------- Object Locations ----------------------------- #
            # Side View
            predicted_frame = annotate.mark_object_center(
                predicted_frame,
                (side[0]+bound_corners[2][0], side[1]+bound_corners[0][1]),
                (255, 0, 0)
            )

            side_crop = json.loads(predicted['side_crop'])
            top_crop = json.loads(predicted['top_crop'])

            # side_crop = [float(i) for i in side_crop]
            # top_crop = [float(i) for i in top_crop]

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

            # --------------------------- object Classification -------------------------- #
            predictions = dict(predicted['predictions'])

            design = predictions["design"][0]
            design_confidence = predictions["design"][1]
            category = predictions["category"][0]
            category_confidence = predictions["category"][1]

            if predictions is not None:

                if design_confidence < 60 or category_confidence < 60:
                    predicted_frame = cv2.putText(
                        predicted_frame,
                        "CONFIDENCE TOO LOW",
                        (predicted_frame.shape[1]//3, 200),
                        cv2.FONT_HERSHEY_DUPLEX, 4, (128, 128, 128), 5
                    )

                else:
                    predicted_frame = cv2.putText(
                        predicted_frame,
                        f"Design | #{design} | {design_confidence:.2f}%",
                        (predicted_frame.shape[1]//3, 200),
                        cv2.FONT_HERSHEY_DUPLEX, 2, (0, 0, 255), 5
                    )

                    predicted_frame = cv2.putText(
                        predicted_frame,
                        f"Category | {category} | {category_confidence:.2f}%",
                        (predicted_frame.shape[1]//3, 300),
                        cv2.FONT_HERSHEY_DUPLEX, 2, (0, 0, 255), 5
                    )

        else:

            predicted_frame = cv2.putText(
                predicted_frame,
                "LEGO NOT FOUND",
                (predicted_frame.shape[1]//3, 200),
                cv2.FONT_HERSHEY_DUPLEX, 4, (128, 128, 128), 5
            )

        # Display part velocity in lower left
        predicted_frame = cv2.putText(
            predicted_frame,
            f"Part Velocity: {config.part_velocity:.2f} in/s",
            (20, predicted_frame.shape[0]-200),
            cv2.FONT_HERSHEY_DUPLEX, 3, (255, 0, 0), 5
        )

        # Display FPS in the upper right
        predicted_frame = cv2.putText(
            predicted_frame,
            f"FPS: {session_stats.fps()}",
            (predicted_frame.shape[1]-500, 100),
            cv2.FONT_HERSHEY_DUPLEX, 3, (255, 0, 0), 5
        )

        redis_db.add_frame("annotated", predicted_frame)
