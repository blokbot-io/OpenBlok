
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


def combined_roi_views(image, side_rect, top_rect):
    '''
    Compensates for missed mixes to ensure:
    - top view as a h:w ratio of 1:1
    - side view h is equal to top view h
    - side view as a h:w ratio of 1:2
    '''
    (side_tl, side_tr, side_br, side_bl) = side_rect
    (top_tl, top_tr, top_br, top_bl) = top_rect
    # Calculate the max height for the side and top views then get the average.

    # Side Max Height
    side_heightA = np.sqrt(((side_tr[0] - side_br[0]) ** 2) + ((side_tr[1] - side_br[1]) ** 2))
    side_heightB = np.sqrt(((side_tl[0] - side_bl[0]) ** 2) + ((side_tl[1] - side_bl[1]) ** 2))
    side_maxHeight = max(int(side_heightA), int(side_heightB))

    # Top Max Height
    top_heightA = np.sqrt(((top_tr[0] - top_br[0]) ** 2) + ((top_tr[1] - top_br[1]) ** 2))
    top_heightB = np.sqrt(((top_tl[0] - top_bl[0]) ** 2) + ((top_tl[1] - top_bl[1]) ** 2))
    top_maxHeight = max(int(top_heightA), int(top_heightB))

    average_height = int((side_maxHeight + top_maxHeight) / 2)

    # Subtract 1 if average_height is not divisible by 2
    if average_height % 2 != 0:
        average_height -= 1

    side_dst = np.array([
        [0, 0],
        [average_height/2 - 1, 0],
        [average_height/2 - 1, average_height - 1],
        [0, average_height - 1]], dtype="float32")

    top_dst = np.array([
        [0, 0],
        [average_height - 1, 0],
        [average_height - 1, average_height - 1],
        [0, average_height - 1]], dtype="float32")

    side_M = cv2.getPerspectiveTransform(side_rect, side_dst)
    top_M = cv2.getPerspectiveTransform(top_rect, top_dst)

    side_warped = cv2.warpPerspective(image, side_M, (int(average_height/2), average_height))
    top_warped = cv2.warpPerspective(image, top_M, (average_height, average_height))

    return np.concatenate((side_warped, top_warped), axis=1)


# time_now = time.time()
# warped_side = four_point_transform(sampled_image, side_rect)
# warped_top = four_point_transform(sampled_image, top_rect)
# print("Time to transform: {}".format(time.time() - time_now))

# # show the original and warped images

# cv2.namedWindow("Side View ROI", cv2.WINDOW_NORMAL)
# cv2.imshow("Side View ROI", warped_side)

# cv2.namedWindow("Top View ROI", cv2.WINDOW_NORMAL)
# cv2.imshow("Top View ROI", warped_top)


time_start = time.time()
combined_roi = combined_roi_views(sampled_image, side_rect, top_rect)
print(f"Time to transform: {time.time() - time_start}")

cv2.namedWindow("Combined View ROI", cv2.WINDOW_NORMAL)
cv2.imshow("Combined View ROI", combined_roi)

cv2.waitKey(0)
cv2.destroyAllWindows()
