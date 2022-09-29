''' Module | Calibrate '''

import config

from bloks import camera
from bloks.utils import get_aruco, get_aruco_details


def rotation_correction():
    '''
    Corrects for the rotation of the camera.
    '''
    if config.rotational_offset is None:
        frame = camera.grab_frame()[0]  # Grab frame
        marker_locations, marker_ids = get_aruco(frame)[:2]
        aruco_center_x, aruco_center_y, _, angle_offset = get_aruco_details(
            marker_locations, marker_ids, 0)  # pylint: disable=C0301

        config.rotational_offset = aruco_center_x, aruco_center_y, angle_offset


def calibration():
    '''
    Startup calibration, returns true if successful, false if not.
    '''
    # 3 Attempt to get the ArUco marker locations
    for _ in range(3):
        frame, frame_time = camera.grab_frame()
        marker_locations = get_aruco(frame)[0]
        if marker_locations is not None:
            break

        print("No ArUco detected, trying again.")

    if config.AruCo_corners is not None:
        rotation_correction()
        return True

    return False
