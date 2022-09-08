''' Main program for OpenBlok '''

import signal
import threading

import config

from bloks import camera, display, precheck


print("INFO | OpenBlok Loading...")

# ---------------------------------------------------------------------------- #
#                              Flags and Variables                             #
# ---------------------------------------------------------------------------- #
config.rotational_offset = None         # Degrees to rotate frame for alignment.

config.requested_frame = None           # Flag | None to request a frame, else contains the frame.

config.enable_sine_wave = False         # TEMP TO TEST

config.AruCo_corners = None             # Variable | AruCo Marker Corners
config.AruCo_ids = None                 # Variable | AruCo Marker IDs
config.AruCo_rejected = None            # Variable | AruCo Markers Rejected
config.AruCo_center_x = None            # Variable | AruCo Marker Center X
config.AruCo_center_y = None            # Variable | AruCo Marker Center Y
config.AruCo_px_per_inch = None         # Variable | AruCo Marker Pixels Per Inch
config.AruCo_angle_offset = None        # Variable | AruCo Marker Angle Offset

check_results = []
check_results.append(precheck.validate_requirements())
# check_results.append(precheck.peripheral_check())

if False in check_results:
    print("OpenBlok cannot be run, please check the requirements and peripherals")
    exit()

# ---------------------------------------------------------------------------- #
#                                 Start Threads                                #
# ---------------------------------------------------------------------------- #
# Camera Thread
start_camera = threading.Thread(target=camera.continuous_capture)
start_camera.start()
print("INFO | Camera thread started.")

# Display Thread
# start_display = threading.Thread(target=display.show)
# start_display.start()

display.predict_and_show_thread()

print("Starting Infinite Loop...")
signal.pause()      # Run until interrupted.
