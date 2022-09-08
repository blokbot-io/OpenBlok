'''
Frame preprocessing, takes in raw frame and returns frame sections.
'''

import numpy as np

from .bounding_areas import bounding_boxes


def capture_regions(frame):
    '''
    Capture regions from frame.
    top_ul - top upper left (x,y)
    top_ll - top lower left (x,y)
    side_ul - side upper left (x,y)
    side_ll - side lower left (x,y)
    '''
    top_ul, top_ll, side_ul, side_ll = bounding_boxes()
    side_crop = frame[side_ul[1]:side_ll[1], side_ul[0]:side_ll[0]]
    top_crop = frame[top_ul[1]:top_ll[1], top_ul[0]:top_ll[0]]

    combined = np.concatenate((side_crop, top_crop), axis=1)

    return combined
