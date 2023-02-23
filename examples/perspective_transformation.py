
import time

import numpy as np
import cv2

from mark_regions import calculated_roi_corners, sampled_image

view_points = calculated_roi_corners()

side_rect = np.array([
    view_points["svtl"][0:2],
    view_points["svtr"][0:2],
    view_points["svbr"][0:2],
    view_points["svbl"][0:2]], dtype=np.float32)

top_rect = np.array([
    view_points["tvtl"][0:2],
    view_points["tvtr"][0:2],
    view_points["tvbr"][0:2],
    view_points["tvbl"][0:2]], dtype=np.float32)


def four_point_transform(image, rect):
    # obtain a consistent order of the points and unpack them
    # individually

    (tl, tr, br, bl) = rect
    # compute the width of the new image, which will be the
    # maximum distance between bottom-right and bottom-left
    # x-coordiates or the top-right and top-left x-coordinates
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))
    # compute the height of the new image, which will be the
    # maximum distance between the top-right and bottom-right
    # y-coordinates or the top-left and bottom-left y-coordinates
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))
    # now that we have the dimensions of the new image, construct
    # the set of destination points to obtain a "birds eye view",
    # (i.e. top-down view) of the image, again specifying points
    # in the top-left, top-right, bottom-right, and bottom-left
    # order
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")
    # compute the perspective transform matrix and then apply it
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    # return the warped image
    return warped


time_now = time.time()
warped_side = four_point_transform(sampled_image, side_rect)
warped_top = four_point_transform(sampled_image, top_rect)
print("Time to transform: {}".format(time.time() - time_now))

# show the original and warped images

cv2.namedWindow("Side View ROI", cv2.WINDOW_NORMAL)
cv2.imshow("Side View ROI", warped_side)

cv2.namedWindow("Top View ROI", cv2.WINDOW_NORMAL)
cv2.imshow("Top View ROI", warped_top)

cv2.waitKey(0)
cv2.destroyAllWindows()
