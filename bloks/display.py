'''
All in one file for the display and prediction.
TODO:
    - Break the visualization into a separate file.
'''
# pylint: disable=R0914,C2801,R0915

import os
import threading
from decimal import Decimal

import cv2
import config
import numpy as np
from screeninfo import get_monitors  # Required to get monitor info

from bloks import serial  # camera, upload
from bloks.utils import annotate, preprocess, stats, bounding_boxes, crop_square
from modules import ob_storage

from modeled import location, e2e

redis_db = ob_storage.RedisStorageManager()


def predict_and_show():
    '''
    Results are displayed on the screen.
    Grabs a frame and then predicts the blok.
    '''
    session_stats = stats.Stats()

    # --------------------------- Display Configuration -------------------------- #
    if os.environ.get('DISPLAY', '') == '':
        os.environ.__setitem__('DISPLAY', ':0')
    monitor = get_monitors()[0]  # Return monitor parameters (width, height)

    bin_schedule = None

    location_model = location.LocationInference()
    e2e_model = e2e.PartInference()

    # ---------------------------- Identification Loop --------------------------- #
    while True:
        # frame, frame_time = camera.grab_frame()     # Grab frame
        next_frame = redis_db.get_frame("rotated")
        frame = next_frame['frame']
        frame_time = next_frame['timestamp']

        frame_time = Decimal(frame_time)            # Copy frame & time
        session_stats.add_frame_time(frame_time)    # Add frame time to stats

        preprocessed_frame = preprocess.capture_regions(frame)      # Preprocess frame
        # Frame to add annotations to
        combined_layers = np.copy(frame)

        # threading.Thread(
        #     target=upload.stream_upload,
        #     args=(
        #         "conveyor", f"raw/{int(frame_time)}.png",
        #         cv2.imencode(
        #             '.png', preprocessed_frame,
        #             [int(cv2.IMWRITE_PNG_COMPRESSION), 0]
        #         )[1].tostring(),
        #         'image/png'
        #     )
        # ).start()

        # Marker Layer
        cv2.aruco.drawDetectedMarkers(
            combined_layers, config.AruCo_corners, config.AruCo_ids)

        # Split Line Layer
        cut_distance = int(config.AruCo_center_x +
                           (config.mirror_offset*config.AruCo_px_per_inch))
        cv2.line(combined_layers, (cut_distance, 0),
                 (cut_distance, frame.shape[0]), (0, 0, 255), 2)

        # Bounding Box Layer
        bound_corners = bounding_boxes()
        combined_layers = annotate.bounding_areas(
            combined_layers, bound_corners)

        # Get Object Locations
        side, top = location_model.get_location(preprocessed_frame)

        if 0 not in [side[0], side[1], top[0], top[1]] and top[0] > preprocessed_frame.shape[1]//3:
            top[0] = top[0] - preprocessed_frame.shape[1]//3

            # ----------------------------- Object Locations ----------------------------- #
            # Side View
            combined_layers = annotate.mark_object_center(
                combined_layers,
                (side[0]+bound_corners[2][0], side[1]+bound_corners[0][1]),
                (255, 0, 0)
            )

            side_crop = crop_square(
                preprocessed_frame[:, :preprocessed_frame.shape[1]//3],
                (side[0], side[1])
            )

            combined_layers = annotate.visualize_crop(
                combined_layers,
                (side_crop[1][0]+bound_corners[2][0],
                 side_crop[1][1]+bound_corners[2][1]),
                (side_crop[2][0]+bound_corners[2][0],
                 side_crop[2][1]+bound_corners[2][1]),
                (255, 0, 0)
            )

            # Top View
            combined_layers = annotate.mark_object_center(
                combined_layers,
                (top[0]+bound_corners[0][0], top[1]+bound_corners[0][1])
            )

            top_crop = crop_square(
                preprocessed_frame[:, preprocessed_frame.shape[1]//3:],
                (top[0], top[1])
            )

            combined_layers = annotate.visualize_crop(
                combined_layers,
                (top_crop[1][0]+bound_corners[0][0],
                 top_crop[1][1]+bound_corners[0][1]),
                (top_crop[2][0]+bound_corners[0][0],
                 top_crop[2][1]+bound_corners[0][1])
            )

            # --------------------------- object Classification -------------------------- #
            view_concatenated = np.concatenate(
                (side_crop[0], top_crop[0]), axis=1)
            predictions = e2e_model.get_predictions(view_concatenated)
            design = predictions["design"][0]
            design_confidence = predictions["design"][1]
            category = predictions["category"][0]
            category_confidence = predictions["category"][1]

            if predictions is not None:

                if design_confidence < 60 or category_confidence < 60:
                    combined_layers = cv2.putText(
                        combined_layers,
                        "CONFIDENCE TOO LOW",
                        (combined_layers.shape[1]//3, 200),
                        cv2.FONT_HERSHEY_DUPLEX, 4, (128, 128, 128), 5
                    )

                else:
                    combined_layers = cv2.putText(
                        combined_layers,
                        f"Design | #{design} | {design_confidence:.2f}%",
                        (combined_layers.shape[1]//3, 200),
                        cv2.FONT_HERSHEY_DUPLEX, 2, (0, 0, 255), 5
                    )

                    combined_layers = cv2.putText(
                        combined_layers,
                        f"Category | {category} | {category_confidence:.2f}%",
                        (combined_layers.shape[1]//3, 300),
                        cv2.FONT_HERSHEY_DUPLEX, 2, (0, 0, 255), 5
                    )

                    # Set bin location to prediction
                    bin_schedule = serial.update_position_schedule(
                        frame_time, top[0],
                        design, design_confidence
                    )

                    # # Save procesed frame
                    # cv2.imwrite(f"/opt/toupload/{int(frame_time)}.png", preprocessed_frame)

        else:

            combined_layers = cv2.putText(
                combined_layers,
                "LEGO NOT FOUND",
                (combined_layers.shape[1]//3, 200),
                cv2.FONT_HERSHEY_DUPLEX, 4, (128, 128, 128), 5
            )
        if bin_schedule is not None:
            for count, next_bin in enumerate(bin_schedule):
                combined_layers = cv2.putText(
                    combined_layers,
                    f"Bin #{next_bin[0]}",
                    (20, (count*60)+60),
                    cv2.FONT_HERSHEY_DUPLEX, 2, (255, 0, 0), 5
                )

        # Display part velocity in lower left
        combined_layers = cv2.putText(
            combined_layers,
            f"Part Velocity: {config.part_velocity:.2f} in/s",
            (20, combined_layers.shape[0]-200),
            cv2.FONT_HERSHEY_DUPLEX, 3, (255, 0, 0), 5
        )

        # Display FPS in the upper right
        combined_layers = cv2.putText(
            combined_layers,
            f"FPS: {session_stats.fps()}",
            (combined_layers.shape[1]-500, 100),
            cv2.FONT_HERSHEY_DUPLEX, 3, (255, 0, 0), 5
        )

        # ----------------------------- Display ----------------------------- #
        # Resize image to fit monitor (does not maintain aspect ratio)
        frame_resized = cv2.resize(
            combined_layers, (monitor.width, monitor.height))

        # ----------------------------- Display Image ------------------------------- #
        # cv2.imshow('Combined', frame_resized)

        # if cv2.waitKey(10) & 0xFF == ord('q'):
        #     break

    cv2.destroyAllWindows()


# ---------------------------------------------------------------------------- #
#                                Thread Controls                               #
# ---------------------------------------------------------------------------- #
def predict_and_show_stop():
    '''
    Ends identification process and closes the view window.
    '''
    config.identifying = False


def predict_and_show_thread():
    '''
    Calls the predict_and_show function in a new thread.
    '''
    config.identifying = True
    start_identifying = threading.Thread(target=predict_and_show)
    start_identifying.start()
