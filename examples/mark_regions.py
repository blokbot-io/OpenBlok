'''
OpenBlok | examples | mark_regions.py

Opens the raw-no_part.png image and marks the following regions:
- AruCo marker
- Side View Box
- Top View Box
'''

import time
import math
import statistics

import cv2
from cv2 import aruco

from distance_calculations import (intersectionPoint,
                                   mtl_svtl, mtr_svtl, mbr_svtl, mbl_svtl,
                                   mtl_svtr, mtr_svtr, mbr_svtr, mbl_svtr,
                                   mtl_svbl, mtr_svbl, mbr_svbl, mbl_svbl,
                                   mtl_svbr, mtr_svbr, mbr_svbr, mbl_svbr,
                                   mtl_tvtl, mtr_tvtl, mbr_tvtl, mbl_tvtl,
                                   mtl_tvtr, mtr_tvtr, mbr_tvtr, mbl_tvtr,
                                   mtl_tvbl, mtr_tvbl, mbr_tvbl, mbl_tvbl,
                                   mtl_tvbr, mtr_tvbr, mbr_tvbr, mbl_tvbr,
                                   )

TEST_IMAGE = "examples/sample_images/raw-no_part.png"

# Load the image
sampled_image = cv2.imread(TEST_IMAGE)


# ------------------------------- AruCo Marker ------------------------------- #
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
parameters = aruco.DetectorParameters()
# parameters.adaptiveThreshWinSizeMin = 300  # 3
# parameters.adaptiveThreshWinSizeMax = 900  # 23
# parameters.adaptiveThreshWinSizeStep = 3  # 10
parameters.adaptiveThreshConstant = 30  # 7
# parameters.cornerRefinementMethod = aruco.CORNER_REFINE_APRILTAG
# parameters.cornerRefinementWinSize = 20  # 5
# # parameters.cornerRefinementMaxIterations = 100  # 30
# parameters.cornerRefinementMinAccuracy = 0.04  # 0.1
# parameters.polygonalApproxAccuracyRate = 0.05  # .05
# parameters.maxErroneousBitsInBorderRate = 0.2  # 0.35
# parameters.errorCorrectionRate = 1.5  # 0.6
# parameters.minDistanceToBorder = 1  # 3
# parameters.aprilTagQuadSigma = 0.2  # 0.0

start_time = time.time()

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

print(f"Time to detect AruCo marker: {time.time() - start_time} seconds")
new_time = time.time()

# print(px_per_inch)

# print(f"Top Left: {top_left}")
# print(f"Top Right: {top_right}")
# print(f"Bottom Left: {bottom_left}")

svtl_roi_corner = intersectionPoint(
    (top_right[0], top_right[1], mtl_svtl*px_per_inch),
    (bottom_left[0], bottom_left[1], mbr_svtl*px_per_inch),
    (top_left[0], top_left[1], mbl_svtl*px_per_inch),
)

# print(f"time to calculate intersection: {time.time() - new_time} seconds")
# print(f"stvl ROI Corner: {svtl_roi_corner.x[0]}, {svtl_roi_corner.x[1]}")

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

print(f"Time to detect ROI corners: {time.time() - new_time} seconds")
print(f"Time to process: {time.time() - start_time} seconds")

# ----------------------------- Apply Annotations ---------------------------- #
# AruCo Marker
cv2.aruco.drawDetectedMarkers(sampled_image, aruco_corners, aruco_ids)

# Marker Corners
cv2.circle(sampled_image, (int(top_right[0]), int(top_right[1])), 10, (0, 0, 255), -1)  # mtl
# cv2.circle(sampled_image, (int(bottom_left[0]), int(bottom_left[1])), 10, (0, 0, 255), -1)  # mbr
# cv2.circle(sampled_image, (int(top_left[0]), int(top_left[1])), 10, (0, 0, 255), -1)  # mbl

# ROI Corners
cv2.circle(sampled_image, (int(svtl_roi_corner.x[0]), int(
    svtl_roi_corner.x[1])), 20, (255, 0, 255), -1)

cv2.circle(sampled_image, (int(svtr_roi_corner.x[0]), int(
    svtr_roi_corner.x[1])), 20, (255, 0, 255), -1)

cv2.circle(sampled_image, (int(svbl_roi_corner.x[0]), int(
    svbl_roi_corner.x[1])), 20, (255, 0, 255), -1)

cv2.circle(sampled_image, (int(svbr_roi_corner.x[0]), int(
    svbr_roi_corner.x[1])), 20, (255, 0, 255), -1)

cv2.circle(sampled_image, (int(tvtl_roi_corner.x[0]), int(
    tvtl_roi_corner.x[1])), 20, (255, 0, 255), -1)

cv2.circle(sampled_image, (int(tvtr_roi_corner.x[0]), int(
    tvtr_roi_corner.x[1])), 20, (255, 0, 255), -1)

cv2.circle(sampled_image, (int(tvbl_roi_corner.x[0]), int(
    tvbl_roi_corner.x[1])), 20, (255, 0, 255), -1)

cv2.circle(sampled_image, (int(tvbr_roi_corner.x[0]), int(
    tvbr_roi_corner.x[1])), 20, (255, 0, 255), -1)

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
