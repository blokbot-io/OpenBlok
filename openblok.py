''' Main program for OpenBlok '''

import sys
import signal
import threading
from queue import Queue

import config

from bloks import camera, calibrate, display, precheck, serial, updater


print("INFO | OpenBlok Loading...")

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
threading.Thread(target=camera.continuous_capture).start()
print("INFO | Camera thread started.")

# Start Serial Listener
threading.Thread(target=serial.serial_listener).start()
print("Serial listener thread started.")

# Start Carousel Position Thread
threading.Thread(target=serial.carousel_position).start()
print("INFO | Carousel position thread started.")

# Display Thread
# start_display = threading.Thread(target=display.show)
# start_display.start()


# ---------------------------------------------------------------------------- #
#                                  Calibration                                 #
# ---------------------------------------------------------------------------- #
if calibrate.calibration():
    print("INFO | Calibration successful.")


# ---------------------------------------------------------------------------- #
#                                   Main Loop                                  #
# ---------------------------------------------------------------------------- #
display.predict_and_show_thread()
print("Starting Infinite Loop...")
signal.pause()      # Run until interrupted.
