''' Manages the cv2 output for the display module '''
# pylint: disable=C2801


import os
import sys

import cv2
import numpy as np
from screeninfo import get_monitors  # Required to get monitor info

from display import initialization

# --------------------------- Display Configuration -------------------------- #
if os.environ.get('DISPLAY', '') == '':
    os.environ.__setitem__('DISPLAY', ':0')
monitor = get_monitors()[0]  # Return monitor parameters (width, height)

# Create a canvas to draw on
canvas = np.zeros_like(np.zeros((monitor.height, monitor.width, 3), np.uint8))

initialization.add_title(canvas)

cv2.imshow('canvas', canvas)

if cv2.waitKey(1) & 0xFF == ord('q'):
    cv2.destroyAllWindows()
    sys.exit()
