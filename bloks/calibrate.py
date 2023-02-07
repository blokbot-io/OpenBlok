''' Module | Calibrate '''

import config

# from bloks import camera
from bloks.utils import get_aruco, get_aruco_details
from modules import ob_storage

metadata_storage = ob_storage.LocalStorageManager()
redis_db = ob_storage.RedisStorageManager()


def rotation_correction():
    '''
    Corrects for the rotation of the camera.
    '''
    if config.rotational_offset is None:
        frame = redis_db.get_frame("raw")['frame']  # Grab frame

        marker_locations, marker_ids = get_aruco(frame)[:2]
        aruco_center_x, aruco_center_y, _, angle_offset = get_aruco_details(
            marker_locations, marker_ids, 0)  # pylint: disable=C0301

        rotational_offset = {
            "aruco_center_x": aruco_center_x,
            "aruco_center_y": aruco_center_y,
            "angle_offset": angle_offset
        }
        metadata_storage.session_metadata(rotational_offset)

        config.rotational_offset = rotational_offset


def calibration():
    '''
    Startup calibration, returns true if successful, false if not.
    '''
    # 3 Attempt to get the ArUco marker locations
    for _ in range(3):
        frame = redis_db.get_frame("raw")['frame']

        marker_locations = get_aruco(frame)[0]
        if marker_locations is not None:
            break

        print("No ArUco detected, trying again.")

    if config.AruCo_corners is not None:
        rotation_correction()
        return True

    return False
