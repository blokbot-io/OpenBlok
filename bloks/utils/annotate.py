''' Utils | Annotate '''

import cv2
import numpy as np


def bounding_areas(frame, bounding_corners):
    '''
    Returns an image depicting the view areas
    '''
    visualize_areas = np.zeros_like(frame, np.uint8)

    # --------------------------- Top View Bounding Box -------------------------- #
    cv2.rectangle(visualize_areas,
                  bounding_corners[0],
                  bounding_corners[1],
                  (0, 255, 0), cv2.FILLED
                  )

    # -------------------------- Side View Bounding Box -------------------------- #
    cv2.rectangle(visualize_areas,
                  bounding_corners[2],
                  bounding_corners[3],
                  (255, 0, 0), cv2.FILLED
                  )

    # ------------------------------ Combine Visuals ----------------------------- #
    alpha = 0.5
    mask = visualize_areas.astype(bool)
    frame[mask] = cv2.addWeighted(frame, alpha, visualize_areas, 1 - alpha, 0)[mask]

    return frame


def masked_areas(frame, mask):
    '''
    Returns the showing the masked background difference in red.
    '''
    visualize_areas = np.zeros_like(frame, np.uint8)
    cv2.rectangle(visualize_areas,
                  (0, 0),
                  (frame.shape[1], frame.shape[0]),
                  (0, 0, 255), cv2.FILLED
                  )

    if frame.shape != mask.shape:
        new_mask = np.zeros_like(frame, np.uint8)
        new_mask = cv2.cvtColor(new_mask, cv2.COLOR_BGR2GRAY)

        bounding_corners = bounding_boxes()

        new_mask[
            bounding_corners[0][1]:bounding_corners[1][1],
            bounding_corners[0][0]:bounding_corners[0][0] + mask[:, mask.shape[1]//3:].shape[1]
        ] = mask[:, mask.shape[1]//3:]

        new_mask[
            bounding_corners[2][1]:bounding_corners[3][1],
            bounding_corners[2][0]:bounding_corners[2][0] + mask[:, :mask.shape[1]//3].shape[1]
        ] = mask[:, :mask.shape[1]//3]

        mask = new_mask

    visualize_areas = cv2.bitwise_and(visualize_areas, visualize_areas, mask=mask)

    alpha = .7
    mask = mask.astype(bool)
    frame[mask] = cv2.addWeighted(frame, alpha, visualize_areas, 1 - alpha, 0)[mask]

    return frame



def mark_object_center(frame, object_center, color=(0, 255, 0)):
    '''
    Returns the frame with a blue dot at the object center.
    '''
    cv2.circle(frame, object_center, 10, color, -1)
    return frame


def visualize_crop(frame, top_left, bottom_right, color=(0, 255, 0)):
    '''
    Returns the frame with a red rectangle showing the crop area.
    '''
    cv2.rectangle(frame,
                  top_left,
                  bottom_right,
                  color, 5
                  )
    return frame
