'''
All in one file for the display and prediction.
TODO:
    - Break the visualization into a separate file.
'''

import os
import time
import threading
from decimal import Decimal

import cv2
import config
import numpy as np
from screeninfo import get_monitors  # Required to get monitor info


from bloks import camera


from bloks.utils import annotate, preprocess, bounding_boxes


from modeled import location

def predict_and_show():
    '''
    Results are displayed on the screen.
    Grabs a frame and then predicts the blok.
    '''
    # --------------------------- Display Configuration -------------------------- #
    if os.environ.get('DISPLAY', '') == '':
        os.environ.__setitem__('DISPLAY', ':0')
    monitor = get_monitors()[0]  # Return monitor parameters (width, height)

    part_in_frame = True  # Flag to indicate if a part is in the frame

    # ---------------------------- Identification Loop --------------------------- #
    while True:
        time_now = time.time()  # Get the current time

        frame, frame_time = camera.grab_frame()                # Grab frame
        frame_time = Decimal(frame_time)     # Copy frame & time

        print(f"Time to take frame: {time.time() - time_now}")

        time_now = time.time()  # Get the current time

        preprocessed_frame = preprocess.capture_regions(frame)      # Preprocess frame
        # combined_layers = np.copy(frame)                            # Frame to add annotations to

        # ------------------------------ Save the frame ------------------------------ #
        cv2.imwrite(f"/opt/stream/{int(frame_time)}.png", preprocessed_frame, [cv2.IMWRITE_PNG_COMPRESSION, 0])

        print(f"Time to preprocess frame: {time.time() - time_now}")

        # Marker Layer
        # cv2.aruco.drawDetectedMarkers(combined_layers, config.AruCo_corners, config.AruCo_ids)

        # Split Line Layer
        # cut_distance = int(config.AruCo_center_x + (config.mirror_offset*config.AruCo_px_per_inch))
        # cv2.line(combined_layers, (cut_distance, 0), (cut_distance, frame.shape[0]), (0, 0, 255), 2)

        # Bounding Box Layer
        # bound_corners = bounding_boxes()
        # combined_layers = annotate.bounding_areas(combined_layers, bound_corners)

        # Get Object Locations
        side, top = location.get_location(preprocessed_frame)

        # ----------------------------- Object Locations ----------------------------- #
        # Top View
        try:
            # combined_layers = annotate.mark_object_center(
            #     combined_layers,
            #     (top[0]+bound_corners[0][0],
            #      top[1]+bound_corners[0][1])
            # )

            preprocessed_frame = annotate.mark_object_center(
                preprocessed_frame,
                (top[0], top[1])
            )

            part_in_frame = True
        except (TypeError, IndexError, cv2.error):
            if part_in_frame:
                print("INFO | No top view center found, getting next frame.")
                part_in_frame = False
            continue

        # Side View
        try:
            # combined_layers = annotate.mark_object_center(
            #     combined_layers,
            #     (side[0]+bound_corners[2][0],
            #      side[1]+bound_corners[0][1]),
            #     (255, 0, 0)
            # )

            preprocessed_frame = annotate.mark_object_center(
                preprocessed_frame,
                (side[0], side[1]),
                (255, 0, 0)
            )

            part_in_frame = True
        except (TypeError, IndexError, cv2.error):
            if part_in_frame:
                print("INFO | No side view center found, getting next frame.")
                part_in_frame = False
            continue




        # ----------------------------- Display ----------------------------- #
        # Resize image to fit monitor
        # frame_resized = cv2.resize(combined_layers, (monitor.width, monitor.height))
        frame_resized = cv2.resize(preprocessed_frame, (monitor.width, monitor.height))

        # ----------------------------- Display Image ------------------------------- #
        cv2.imshow('Combined', frame_resized)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

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
