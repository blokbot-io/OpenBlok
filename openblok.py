''' Main program for OpenBlok '''

import sys
import signal
import threading
import multiprocessing
from queue import Queue

import config

from bloks import camera, calibrate, precheck, serial, updater  # , display
from sub_processes import ob_rotate_frame, ob_roi_frame, ob_predictions, ob_annotate_frame
from modules import ob_storage

# multiprocessing.set_start_method('spawn')

print("INFO | OpenBlok Loading...")

redis_db = ob_storage.RedisStorageManager()
redis_db.clear_db()

# ---------------------------------------------------------------------------- #
#                              Flags and Variables                             #
# ---------------------------------------------------------------------------- #
config.rotational_offset = None         # Degrees to rotate frame for alignment.

config.frame_queue = Queue(maxsize=10)  # Queue of frames to be displayed.

config.requested_frame = None   # Flag | None to request a frame, else contains the frame.

config.enable_sine_wave = False         # TEMP TO TEST

config.AruCo_corners = None             # Variable | AruCo Marker Corners
config.AruCo_ids = None                 # Variable | AruCo Marker IDs
config.AruCo_rejected = None            # Variable | AruCo Markers Rejected
config.AruCo_center_x = None            # Variable | AruCo Marker Center X
config.AruCo_center_y = None            # Variable | AruCo Marker Center Y
config.AruCo_px_per_inch = None         # Variable | AruCo Marker Pixels Per Inch
config.AruCo_angle_offset = None        # Variable | AruCo Marker Angle Offset

config.mirror_offset = 4.075            # Configuration | Mirror Offset
config.marker_y_offset = 0.0            # Configuration | Marker Y Offset
config.y_bounding_offset = 2.250        # Configuration | Y Bounding Offset
config.x_bounding_offset = 0            # Configuration | X Bounding Offset

if not precheck.validate_requirements():
    print("OpenBlok cannot be run, please check the requirements.")
    sys.exit()

# if not precheck.peripheral_check():
#     print("OpenBlok cannot be run, please check the peripherals.")
#     sys.exit()

updater.update_models()  # Update models

# ---------------------------------------------------------------------------- #
#                                 Start Threads                                #
# ---------------------------------------------------------------------------- #
# Camera Thread
# threading.Thread(target=camera.continuous_capture).start()
camera_process = multiprocessing.Process(target=camera.continuous_capture)
camera_process.daemon = True
camera_process.start()
print("INFO | Camera thread started.")

# Start Serial Listener
# threading.Thread(target=serial.serial_listener).start()
# print("Serial listener thread started.")

# Start Carousel Position Thread
# threading.Thread(target=serial.carousel_position).start()
# print("INFO | Carousel position thread started.")

# Display Thread
# start_display = threading.Thread(target=display.show)
# start_display.start()


# ---------------------------------------------------------------------------- #
#                                  Calibration                                 #
# ---------------------------------------------------------------------------- #
if calibrate.calibration():
    print("INFO | Calibration successful.")


# ---------------------------------------------------------------------------- #
#                             Start multiprocessing                            #
# ---------------------------------------------------------------------------- #
for _ in range(2):  # Starts 2 multiprocessing processes to correct for rotation.
    rotate_process = multiprocessing.Process(
        target=ob_rotate_frame.rotation_correction, args=(config.rotational_offset,))
    rotate_process.daemon = True
    rotate_process.start()

roi_process = multiprocessing.Process(target=ob_roi_frame.capture_regions)
roi_process.daemon = True
roi_process.start()

# for _ in range(2):  # Starts 2 multiprocessing processes to predict.
predict_process = multiprocessing.Process(target=ob_predictions.run_models)
predict_process.daemon = True
predict_process.start()

annotate_process = multiprocessing.Process(
    target=ob_annotate_frame.annotations,
    args=(config.AruCo_corners, config.AruCo_ids, config.AruCo_center_x,
          config.mirror_offset, config.AruCo_px_per_inch)
)
annotate_process.daemon = True
annotate_process.start()

# ---------------------------------------------------------------------------- #
#                                   Main Loop                                  #
# ---------------------------------------------------------------------------- #
# display.predict_and_show_thread()
print("Starting Infinite Loop...")
signal.pause()      # Run until interrupted.
