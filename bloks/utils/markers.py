'''
Utils | AruCo Markers
Returns the location of AruCo markers in the image '''
# pylint: disable=E0611

import math
import statistics

import config

from cv2 import aruco


def get_aruco(img):
    '''
    Called to get the location of AruCo markers in the image.
    '''
    if config.AruCo_corners is None:
        # aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)
        aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
        # parameters = aruco.DetectorParameters_create()
        parameters = aruco.DetectorParameters()
        parameters.adaptiveThreshWinSizeMin = 2  # 3
        parameters.adaptiveThreshWinSizeMax = 75  # 23
        parameters.adaptiveThreshWinSizeStep = 15  # 10
        parameters.adaptiveThreshConstant = 15  # 7
        parameters.cornerRefinementMethod = aruco.CORNER_REFINE_APRILTAG
        parameters.cornerRefinementWinSize = 20  # 5
        parameters.cornerRefinementMaxIterations = 100  # 30
        parameters.cornerRefinementMinAccuracy = 0.04  # 0.1
        parameters.polygonalApproxAccuracyRate = 0.05  # .05
        parameters.maxErroneousBitsInBorderRate = 0.5  # 0.35
        parameters.errorCorrectionRate = 1.5  # 0.6
        parameters.minDistanceToBorder = 1  # 3
        parameters.aprilTagQuadSigma = 0.2  # 0.0

        corners, ids, rejected_img_points = aruco.detectMarkers(
            img, aruco_dict,
            parameters=parameters
        )

        if corners is not None:
            config.AruCo_corners = corners
            config.AruCo_ids = ids
            config.AruCo_rejected_img_points = rejected_img_points
        else:
            return None, None, None

    return config.AruCo_corners, config.AruCo_ids, config.AruCo_rejected


def get_aruco_details(marker_locations, marker_ids, selected_id=0):
    '''
    Returns the location of the selected AruCo marker and
    the degrees needed to rotate the frame around the markers center.

    The pixels per inch calculation is based on a 1x1 inch marker.
    '''
    try:
        if config.AruCo_px_per_inch is None:
            for (marker_corner, marker_id) in zip(marker_locations, marker_ids.flatten()):
                if marker_id == selected_id:

                    (top_left, top_right, bottom_right, bottom_left) = marker_corner.reshape((4, 2))

                    top_right = [int(top_right[0]), int(top_right[1])]
                    bottom_right = [int(bottom_right[0]), int(bottom_right[1])]
                    bottom_left = [int(bottom_left[0]), int(bottom_left[1])]
                    top_left = [int(top_left[0]), int(top_left[1])]

                    # Calculate the center of the marker
                    center_x = int((top_left[0] + bottom_right[0]) / 2.0)
                    center_y = int((top_left[1] + bottom_right[1]) / 2.0)

                    # Calculate the angle of the marker
                    hypotenuse = math.dist(top_left, bottom_right)/2
                    triangle_height = center_y - top_left[1]
                    angle_offset = 45 - (abs(math.degrees(math.asin(triangle_height/hypotenuse))))

                    # Calculate the pixels per inch (Assuming 1x1 inch marker)
                    px_per_inch = int(
                        statistics.mean(
                            [
                                math.dist(top_left, top_right), math.dist(
                                    bottom_left, bottom_right),
                                math.dist(top_left, bottom_left), math.dist(top_right, bottom_right)
                            ]
                        )
                    )

                config.AruCo_center_x = center_x
                config.AruCo_center_y = center_y
                config.AruCo_px_per_inch = px_per_inch
                config.AruCo_angle_offset = angle_offset

        return [
            config.AruCo_center_x, config.AruCo_center_y,
            config.AruCo_px_per_inch, config.AruCo_angle_offset
        ]

    except (UnboundLocalError, AttributeError):
        print("ERROR | get_aruco_details: No AruCo marker detected")
        return None, None, None, None
