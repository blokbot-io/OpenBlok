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


from bloks import camera, serial


from bloks.utils import annotate, preprocess, bounding_boxes, crop_square


from modeled import location, e2e

def predict_and_show():
    '''
    Results are displayed on the screen.
    Grabs a frame and then predicts the blok.
    '''
    # --------------------------- Display Configuration -------------------------- #
    if os.environ.get('DISPLAY', '') == '':
        os.environ.__setitem__('DISPLAY', ':0')
    monitor = get_monitors()[0]  # Return monitor parameters (width, height)

    bin_schedule = None


    # ---------------------------- Identification Loop --------------------------- #
    while True:
        frame, frame_time = camera.grab_frame() # Grab frame
        frame_time = Decimal(frame_time)        # Copy frame & time

        preprocessed_frame = preprocess.capture_regions(frame)      # Preprocess frame
        combined_layers = np.copy(frame)                            # Frame to add annotations to


        # Marker Layer
        cv2.aruco.drawDetectedMarkers(combined_layers, config.AruCo_corners, config.AruCo_ids)

        # Split Line Layer
        cut_distance = int(config.AruCo_center_x + (config.mirror_offset*config.AruCo_px_per_inch))
        cv2.line(combined_layers, (cut_distance, 0), (cut_distance, frame.shape[0]), (0, 0, 255), 2)

        # Bounding Box Layer
        bound_corners = bounding_boxes()
        combined_layers = annotate.bounding_areas(combined_layers, bound_corners)

        # Get Object Locations
        side, top = location.get_location(preprocessed_frame)
        og_top = top.copy()

        if side[0] > 0 and side[1] > 0 and top[0] > 0 and top[1] > 0 and top[0] > preprocessed_frame.shape[1]//3:
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
                (side_crop[1][0]+bound_corners[2][0], side_crop[1][1]+bound_corners[2][1]),
                (side_crop[2][0]+bound_corners[2][0], side_crop[2][1]+bound_corners[2][1]),
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
                (top_crop[1][0]+bound_corners[0][0], top_crop[1][1]+bound_corners[0][1]),
                (top_crop[2][0]+bound_corners[0][0], top_crop[2][1]+bound_corners[0][1])
            )

            # --------------------------- object Classification -------------------------- #
            view_concatenated = np.concatenate((side_crop[0], top_crop[0]), axis=1)
            predictions = e2e.get_predictions(view_concatenated)
            design = predictions["design"][0]
            design_confidence = predictions["design"][1]
            category = predictions["category"][0]
            category_confidence = predictions["category"][1]

            if predictions is not None:

                if design_confidence<60 or category_confidence<60:
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



            # ------------------------------ Save the frame ------------------------------ #
            # cv2.imwrite(f"/opt/stream/{int(frame_time)}_{side[0]}_{side[1]}_{top[0]}_{top[1]}.png", preprocessed_frame, [cv2.IMWRITE_PNG_COMPRESSION, 0])
            # cv2.imwrite(f"/opt/stream/{int(frame_time)}.png", preprocessed_frame, [cv2.IMWRITE_PNG_COMPRESSION, 0])
            # cv2.imwrite(f"/opt/predict/{int(frame_time)}.png", view_concatenated, [cv2.IMWRITE_PNG_COMPRESSION, 0])

        else:

            reduced_size = cv2.resize(preprocessed_frame, (900, 600), interpolation=cv2.INTER_CUBIC)
            cv2.imwrite(f"/opt/stream/{int(frame_time)}_{side[0]}_{side[1]}_{og_top[0]}_{og_top[1]}.png", reduced_size, [cv2.IMWRITE_PNG_COMPRESSION, 0])

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
                    (20, (count*50)+30),
                    cv2.FONT_HERSHEY_DUPLEX, 2, (255, 0, 0), 5
                )

        # Display part velocity in lower left
        combined_layers = cv2.putText(
            combined_layers,
            f"Part Velocity: {config.part_velocity:.2f} in/s",
            (20, combined_layers.shape[0]-200),
            cv2.FONT_HERSHEY_DUPLEX, 3, (255, 0, 0), 5
        )

        # Display the resulting frame
        cv2.imshow('frame', combined_layers)

        # Press Q on keyboard to  exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # ----------------------------- Display ----------------------------- #
        # Resize image to fit monitor (does not maintain aspect ratio)
        frame_resized = cv2.resize(combined_layers, (monitor.width, monitor.height))


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
