import math
import statistics

from cv2 import aruco
from scipy.optimize import least_squares


from . import ob_system

roi_point_distances = ob_system.marker_roi_distances()
print(roi_point_distances["svtl"])

mtl_svtl, mtr_svtl, mbr_svtl, mbl_svtl = roi_point_distances["svtl"]
mtl_svtr, mtr_svtr, mbr_svtr, mbl_svtr = roi_point_distances["svtr"]
mtl_svbl, mtr_svbl, mbr_svbl, mbl_svbl = roi_point_distances["svbl"]
mtl_svbr, mtr_svbr, mbr_svbr, mbl_svbr = roi_point_distances["svbr"]
mtl_tvtl, mtr_tvtl, mbr_tvtl, mbl_tvtl = roi_point_distances["tvtl"]
mtl_tvtr, mtr_tvtr, mbr_tvtr, mbl_tvtr = roi_point_distances["tvtr"]
mtl_tvbl, mtr_tvbl, mbr_tvbl, mbl_tvbl = roi_point_distances["tvbl"]
mtl_tvbr, mtr_tvbr, mbr_tvbr, mbl_tvbr = roi_point_distances["tvbr"]

# ---------------------------------------------------------------------------- #
#                                 Trilateration                                #
# ---------------------------------------------------------------------------- #


def intersectionPoint(point_1, point_2, point_3):
    '''
    Given three points and their distances from a point, find the unknown point.
    '''
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
    intersection_point = least_squares(eq, guess, bounds=bounds, method='dogbox')

    return intersection_point.x


def calculated_roi_corners(frame):
    # ------------------------------- AruCo Marker ------------------------------- #
    aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
    parameters = aruco.DetectorParameters()
    parameters.adaptiveThreshConstant = 30  # 7

    aruco_corners, aruco_ids, rejected_img_points = aruco.detectMarkers(
        frame, aruco_dict,
        parameters=parameters
    )

    for (marker_corner, marker_id) in zip(aruco_corners, aruco_ids.flatten()):
        if marker_id == 0:
            (top_left, top_right, bottom_right, bottom_left) = marker_corner.reshape((4, 2))
            px_per_inch = int(
                statistics.mean(
                    [
                        math.dist(top_left, top_right), math.dist(
                            bottom_left, bottom_right),
                        math.dist(top_left, bottom_left), math.dist(top_right, bottom_right)
                    ]
                )
            )

    svtl_roi_corner = intersectionPoint(
        (top_right[0], top_right[1], mtl_svtl*px_per_inch),
        (bottom_left[0], bottom_left[1], mbr_svtl*px_per_inch),
        (top_left[0], top_left[1], mbl_svtl*px_per_inch),
    )

    svtr_roi_corner = intersectionPoint(
        (top_right[0], top_right[1], mtl_svtr*px_per_inch),
        (bottom_left[0], bottom_left[1], mbr_svtr*px_per_inch),
        (top_left[0], top_left[1], mbl_svtr*px_per_inch),
    )
    # print(f"svtr ROI Corner: {svtr_roi_corner.x[0]}, {svtr_roi_corner.x[1]}")

    # Marker to Side View Bottom Left
    svbl_roi_corner = intersectionPoint(
        (top_right[0], top_right[1], mtl_svbl*px_per_inch),
        (bottom_left[0], bottom_left[1], mbr_svbl*px_per_inch),
        (top_left[0], top_left[1], mbl_svbl*px_per_inch),
    )

    # Marker to Side View Bottom Right
    svbr_roi_corner = intersectionPoint(
        (top_right[0], top_right[1], mtl_svbr*px_per_inch),
        (bottom_left[0], bottom_left[1], mbr_svbr*px_per_inch),
        (top_left[0], top_left[1], mbl_svbr*px_per_inch),
    )

    # Marker to Top View Top Left
    tvtl_roi_corner = intersectionPoint(
        (top_right[0], top_right[1], mtl_tvtl*px_per_inch),
        (bottom_left[0], bottom_left[1], mbr_tvtl*px_per_inch),
        (top_left[0], top_left[1], mbl_tvtl*px_per_inch),
    )

    # Marker to Top View Top Right
    tvtr_roi_corner = intersectionPoint(
        (top_right[0], top_right[1], mtl_tvtr*px_per_inch),
        (bottom_left[0], bottom_left[1], mbr_tvtr*px_per_inch),
        (top_left[0], top_left[1], mbl_tvtr*px_per_inch),
    )

    # Marker to Top View Bottom Left
    tvbl_roi_corner = intersectionPoint(
        (top_right[0], top_right[1], mtl_tvbl*px_per_inch),
        (bottom_left[0], bottom_left[1], mbr_tvbl*px_per_inch),
        (top_left[0], top_left[1], mbl_tvbl*px_per_inch),
    )

    # Marker to Top View Bottom Right
    tvbr_roi_corner = intersectionPoint(
        (top_right[0], top_right[1], mtl_tvbr*px_per_inch),
        (bottom_left[0], bottom_left[1], mbr_tvbr*px_per_inch),
        (top_left[0], top_left[1], mbl_tvbr*px_per_inch),
    )

    return {
        "svtl": svtl_roi_corner,
        "svtr": svtr_roi_corner,
        "svbl": svbl_roi_corner,
        "svbr": svbr_roi_corner,
        "tvtl": tvtl_roi_corner,
        "tvtr": tvtr_roi_corner,
        "tvbl": tvbl_roi_corner,
        "tvbr": tvbr_roi_corner,
    }
