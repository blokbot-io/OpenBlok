''' Tools to aid in cropping images. '''
# pylint: disable=R0914

import cv2


def crop_tight(image, corners, padding=0.1):
    '''
    Crop to the smallest square that contains the image.
    '''
    img_crop = image[
        (corners[1]-int(corners[3]*padding)): (corners[1]+(corners[3]+int(corners[3]*padding))),
        (corners[0]-int(corners[2]*padding)): (corners[0]+(corners[2]+int(corners[2]*padding)))
    ]
    return img_crop


def crop_square(frame, location_xy, cut_distance=0, pixels=600):
    '''
    Crop to a square of the given size length and width of given pixels.
    Offset part center to maintain minimum crop size.
    If final crop size differs from pixels, resize to match pixels.
    '''
    try:
        # ------------------------------ Crop Dimension ------------------------------ #
        final_width = pixels
        final_height = pixels
        half_width = final_width // 2
        half_height = final_height // 2

        # ---------------------------------------------------------------------------- #
        #                                    Offsets                                   #
        # ---------------------------------------------------------------------------- #
        frame_height, frame_width = frame.shape[:2]

        # --------------------------------- X Offset --------------------------------- #
        part_center_x = location_xy[0]

        if cut_distance > 0 and part_center_x < cut_distance:
            right_bound = cut_distance
            left_bound = 0
        else:
            right_bound = frame_width
            left_bound = cut_distance if cut_distance > 0 else 0

        if right_bound - part_center_x < half_width:
            part_center_x = right_bound - half_width

        if part_center_x - left_bound < half_width:
            part_center_x = left_bound + half_width

        # Y Offset
        part_center_y = location_xy[1]

        # Y Too Low
        if frame_height - part_center_y < half_height:
            part_center_y = frame_height - half_height

        # Y Too High
        if part_center_y < half_height:
            part_center_y = half_height

        # ----------------------------------- Crop ----------------------------------- #
        # frame[y1:y2, x1:x2]
        part_square = frame[
            (part_center_y - half_height): (part_center_y + half_height),
            (part_center_x - half_width): (part_center_x + half_width)
        ]

        # ------------------------------- Final Resize ------------------------------- #
        if part_square.shape[0] != pixels:
            part_square = cv2.resize(part_square, (pixels, pixels), interpolation=cv2.INTER_AREA)

        top_left = [part_center_x - half_width, part_center_y - half_height]
        bottom_right = [part_center_x + half_width, part_center_y + half_height]

        return {
            "croppedFrame": part_square,
            "topLeftCoordinate": top_left,
            "bottomRightCoordinate": bottom_right
        }
    except IndexError as err:
        print(f"Unable to crop square: {err}")
        return None, None, None
