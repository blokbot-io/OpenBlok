'''
OpenBlok | ob_system.py
Responsible for the management and interaction of the system.json file
'''

import math
import json

SYSTEM_FILE = '/opt/OpenBlok/system.json'


def get(key_path, default=None):
    '''
    Get a value from the system.json file
    '''
    return_value = default

    try:
        with open(SYSTEM_FILE, 'r', encoding="UTF-8") as system_file:
            system_info = json.load(system_file)

            if isinstance(key_path, list):
                for key in key_path:
                    system_info = system_info[key]
                return_value = system_info
            else:
                return_value = system_info[key_path]

    except (FileNotFoundError, KeyError) as error:
        print(error)

    return return_value


# ---------------------------------------------------------------------------- #
#                                    Presets                                   #
# ---------------------------------------------------------------------------- #
MARKER_SIZE_IN = 1  # Actual size (l,h) of the marker in inches
MARKER_MIRROR_DISTANCE = 4.075  # Distance from the center of the marker to the mirror intersection in inches
MIRROR_OFFSET_TO_TOP_VIEW = 1  # Distance from the mirror intersection to the top view in inches
TOP_VIEW_HEIGHT = 4.5  # Height of the top view in inches

TOP_VIEW_WIDTH = TOP_VIEW_HEIGHT  # Width of the top view in inches
SIDE_VEW_HEIGHT = TOP_VIEW_HEIGHT  # Height of the side view in inches
SIDE_VIEW_WIDTH = TOP_VIEW_WIDTH / 2  # Width of the side view in inches

ROI_Y_OFFSET = 2.25  # Offset from the center of the marker to the top of the ROI in inches
MARKER_CENTER = [0, 0]  # Set to 0,0 for distance calculations

# ---------------------------------------------------------------------------- #
#                        Corner Coordinate Extrapolation                       #
# ---------------------------------------------------------------------------- #
# Marker
mtl = [
    MARKER_CENTER[0] - (MARKER_SIZE_IN / 2),    # X
    MARKER_CENTER[1] + (MARKER_SIZE_IN / 2)     # Y
]
mtr = [
    MARKER_CENTER[0] + (MARKER_SIZE_IN / 2),    # X
    MARKER_CENTER[1] + (MARKER_SIZE_IN / 2)     # Y
]
mbl = [
    MARKER_CENTER[0] - (MARKER_SIZE_IN / 2),    # X
    MARKER_CENTER[1] - (MARKER_SIZE_IN / 2)     # Y
]
mbr = [
    MARKER_CENTER[0] + (MARKER_SIZE_IN / 2),    # X
    MARKER_CENTER[1] - (MARKER_SIZE_IN / 2)     # Y
]

# Side View
svtr = [
    MARKER_CENTER[0] + MARKER_MIRROR_DISTANCE,  # X
    MARKER_CENTER[1] + ROI_Y_OFFSET             # Y
]
svbr = [
    svtr[0],                                    # X
    svtr[1] - TOP_VIEW_HEIGHT                   # Y
]
svtl = [
    svtr[0] - SIDE_VIEW_WIDTH,
    svtr[1]
]
svbl = [
    svtl[0],
    svbr[1]
]

# Top View
tvtl = [
    MARKER_CENTER[0] + MARKER_MIRROR_DISTANCE + MIRROR_OFFSET_TO_TOP_VIEW,
    MARKER_CENTER[1] + ROI_Y_OFFSET
]
tvtr = [
    tvtl[0] + TOP_VIEW_WIDTH,
    tvtl[1]
]
tvbl = [
    tvtl[0],
    tvtl[1] - TOP_VIEW_HEIGHT
]
tvbr = [
    tvtr[0],
    tvbl[1]
]

# ---------------------------------------------------------------------------- #
#                          Point Distance Calculations                         #
# ---------------------------------------------------------------------------- #
# Marker to Side View Top Left
mtl_svtl = math.dist(mtl, svtl)
mtr_svtl = math.dist(mtr, svtl)
mbl_svtl = math.dist(mbl, svtl)
mbr_svtl = math.dist(mbr, svtl)

# Marker to Side View Top Right
mtl_svtr = math.dist(mtl, svtr)
mtr_svtr = math.dist(mtr, svtr)
mbl_svtr = math.dist(mbl, svtr)
mbr_svtr = math.dist(mbr, svtr)

# Marker to Side View Bottom Left
mtl_svbl = math.dist(mtl, svbl)
mtr_svbl = math.dist(mtr, svbl)
mbl_svbl = math.dist(mbl, svbl)
mbr_svbl = math.dist(mbr, svbl)

# Marker to Side View Bottom Right
mtl_svbr = math.dist(mtl, svbr)
mtr_svbr = math.dist(mtr, svbr)
mbl_svbr = math.dist(mbl, svbr)
mbr_svbr = math.dist(mbr, svbr)

# Marker to Top View Top Left
mtl_tvtl = math.dist(mtl, tvtl)
mtr_tvtl = math.dist(mtr, tvtl)
mbl_tvtl = math.dist(mbl, tvtl)
mbr_tvtl = math.dist(mbr, tvtl)

# Marker to Top View Top Right
mtl_tvtr = math.dist(mtl, tvtr)
mtr_tvtr = math.dist(mtr, tvtr)
mbl_tvtr = math.dist(mbl, tvtr)
mbr_tvtr = math.dist(mbr, tvtr)

# Marker to Top View Bottom Left
mtl_tvbl = math.dist(mtl, tvbl)
mtr_tvbl = math.dist(mtr, tvbl)
mbl_tvbl = math.dist(mbl, tvbl)
mbr_tvbl = math.dist(mbr, tvbl)

# Marker to Top View Bottom Right
mtl_tvbr = math.dist(mtl, tvbr)
mtr_tvbr = math.dist(mtr, tvbr)
mbl_tvbr = math.dist(mbl, tvbr)
mbr_tvbr = math.dist(mbr, tvbr)


def marker_roi_distances():
    '''
    m - marker
    sv - side view
    tv - top view

    t - top
    b - bottom
    l - left
    r - right
    '''
    return {
        "svtl": [mtl_svtl, mtr_svtl, mbr_svtl, mbl_svtl],
        "svtr": [mtl_svtr, mtr_svtr, mbr_svtr, mbl_svtr],
        "svbl": [mtl_svbl, mtr_svbl, mbr_svbl, mbl_svbl],
        "svbr": [mtl_svbr, mtr_svbr, mbr_svbr, mbl_svbr],
        "tvtl": [mtl_tvtl, mtr_tvtl, mbr_tvtl, mbl_tvtl],
        "tvtr": [mtl_tvtr, mtr_tvtr, mbr_tvtr, mbl_tvtr],
        "tvbl": [mtl_tvbl, mtr_tvbl, mbr_tvbl, mbl_tvbl],
        "tvbr": [mtl_tvbr, mtr_tvbr, mbr_tvbr, mbl_tvbr]
    }
