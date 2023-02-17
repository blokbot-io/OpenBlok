'''
OpenBlok | examples | mark_regions.py

Opens the raw-no_part.png image and marks the following regions:
- AruCo marker
- Side View Box
- Top View Box
'''

import math
import statistics

import cv2
from cv2 import aruco

from distance_calculations import intersectionPoint, mtl_svtl, mbr_svtl, mbl_svtl

TEST_IMAGE = "examples/sample_images/raw-no_part.png"

# Load the image
sampled_image = cv2.imread(TEST_IMAGE)

# ------------------------------- AruCo Marker ------------------------------- #
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
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

aruco_corners, aruco_ids, rejected_img_points = aruco.detectMarkers(
    sampled_image, aruco_dict,
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
print(px_per_inch)

print(f"Top Left: {top_left}")
print(f"Top Right: {top_right}")
print(f"Bottom Left: {bottom_left}")

roi_corner = intersectionPoint(
    (top_right[0], top_right[1], mtl_svtl*px_per_inch),
    (bottom_left[0], bottom_left[1], mbr_svtl*px_per_inch),
    (top_left[0], top_left[1], mbl_svtl*px_per_inch),
)
print(f"ROI Corner: {roi_corner.x[0]}, {roi_corner.x[1]}")

# ----------------------------- Apply Annotations ---------------------------- #
# AruCo Marker
cv2.aruco.drawDetectedMarkers(sampled_image, aruco_corners, aruco_ids)

# Marker Corners
cv2.circle(sampled_image, (int(top_right[0]), int(top_right[1])), 10, (0, 0, 255), -1)  # mtl
# cv2.circle(sampled_image, (int(bottom_left[0]), int(bottom_left[1])), 10, (0, 0, 255), -1)  # mbr
# cv2.circle(sampled_image, (int(top_left[0]), int(top_left[1])), 10, (0, 0, 255), -1)  # mbl

# ROI Corners
cv2.circle(sampled_image, (int(roi_corner.x[0]), int(roi_corner.x[1])), 20, (255, 0, 255), -1)

# Intersection circle (for debugging)
cv2.circle(sampled_image, (int(top_right[0]), int(
    top_right[1])), int(mtl_svtl*px_per_inch), (0, 0, 255), 10)

cv2.circle(sampled_image, (int(bottom_left[0]), int(
    bottom_left[1])), int(mbr_svtl*px_per_inch), (0, 0, 255), 10)


# ------------------------------ Display Results ----------------------------- #
cv2.namedWindow("Annotated Output", cv2.WINDOW_NORMAL)
cv2.imshow("Annotated Output", sampled_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
