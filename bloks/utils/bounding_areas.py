''' Returns coordinates for bounding boxes.'''

import config

BOX_WIDTH = 4.5


def bounding_boxes():
    '''
    Returns corner coordinates for the top and side bounding boxes.

    Top Box:
    - Located on right side of the split line
    - 1:1 ratio

    Side Box:
    - Located on the left side of the split line
    - .5 width of top box
    - Same height as top box
    '''
    cut_distance = int(config.AruCo_center_x + (config.mirror_offset * config.AruCo_px_per_inch))
    box_width_pixel = int(config.AruCo_px_per_inch * BOX_WIDTH)

    center_y = config.AruCo_center_y - (config.AruCo_px_per_inch * config.marker_y_offset)  # Pixels
    top_y = int(center_y - (box_width_pixel / 2))  # Pixels

    cut_distance_right_offset = int(cut_distance + (config.AruCo_px_per_inch * .25))

    top_bounding_box_starting_point = (cut_distance_right_offset, top_y)

    top_bounding_box_ending_point = (
        int(cut_distance_right_offset+box_width_pixel),
        int(top_y+box_width_pixel)
    )

    side_bounding_box_starting_point = (
        int(cut_distance - box_width_pixel/2),
        int(top_y)
    )

    side_bounding_box_ending_point = (
        int(cut_distance),
        int(top_y+box_width_pixel)
    )

    return (
        top_bounding_box_starting_point,
        top_bounding_box_ending_point,
        side_bounding_box_starting_point,
        side_bounding_box_ending_point
    )


def bounding_box_contains(top_left, bottom_right, point):
    '''
    Returns true if the bounding box contains the point.
    '''
    if top_left[0] < point[0] < bottom_right[0] and top_left[1] < point[1] < bottom_right[1]:
        return True
    return False


def overlaps_edge(frame_shape, x_pos, y_pos, width, height):
    '''
    Returns true if the bounding box overlaps the edge of the frame.
    '''
    if x_pos <= 0 or y_pos <= 0 or x_pos+width >= frame_shape[1] or y_pos+height >= frame_shape[0]:
        return True
    return False
