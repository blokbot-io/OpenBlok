'''
m - marker
sv - side view
tv - top view

t - top
b - bottom
l - left
r - right
'''

import math
import matplotlib.pyplot as plt
from scipy.optimize import least_squares


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

# ---------------------------------------------------------------------------- #
#                                 Trilateration                                #
# ---------------------------------------------------------------------------- #


def intersectionPoint(point_1, point_2, point_3):

    x1, y1, dist_1 = point_1
    x2, y2, dist_2 = point_2
    x3, y3, dist_3 = point_3

    def eq(g):
        x, y = g

        return (
            (x - x1)**2 + (y - y1)**2 - dist_1**2,
            (x - x2)**2 + (y - y2)**2 - dist_2**2,
            (x - x3)**2 + (y - y3)**2 - dist_3**2
        )

    guess = (3840/2, 2160/2)
    bounds = [[0, 0], [3840, 2160]]
    ans = least_squares(eq, guess, bounds=bounds, method='dogbox')

    return ans


# ans = intersectionPoint(
#     (mtl[0], mtl[1], mtl_svtl),
#     (mbr[0], mbr[1], mbr_svtl),
#     (mbl[0], mbl[1], mbl_svtl)
# )
# print("Center: ", ans.x[0], ans.x[1])

# ---------------------------------------------------------------------------- #
#                                   plotting                                   #
# ---------------------------------------------------------------------------- #
x_points = [
    mtl[0], mtr[0], mbr[0], mbl[0], mtl[0],
    svtr[0], svbr[0], svbl[0], svtl[0],
    tvtl[0], tvtr[0], tvbr[0], tvbl[0], tvtl[0]
]
y_points = [
    mtl[1], mtr[1], mbr[1], mbl[1], mtl[1],
    svtr[1], svbr[1], svbl[1], svtl[1],
    tvtl[1], tvtr[1], tvbr[1], tvbl[1], tvtl[1]
]

figure, axes = plt.subplots()
plt.plot(x_points, y_points, 'ro')

mtlc = plt.Circle((mtl[0], mtl[1]),
                  mtl_svtl, color='r', fill=False, clip_on=False)
mblc = plt.Circle((mbl[0], mbl[1]),
                  mbl_svtl, color='r', fill=False, clip_on=False)
mbrc = plt.Circle((mbr[0], mbr[1]),
                  mbr_svtl, color='r', fill=False, clip_on=False)
mtrc = plt.Circle((mtr[0], mtr[1]),
                  mtr_svtl, color='r', fill=False, clip_on=False)

axes.set_aspect(1)
axes.add_artist(mtlc)
axes.add_artist(mblc)
axes.add_artist(mbrc)
axes.add_artist(mtrc)

# plt.show()
