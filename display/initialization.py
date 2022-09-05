''' Display elements while system is initializing '''

import cv2


def add_title(canvas, title="OpenBlok"):
    '''
    Add tittle to canvas.
    Centered horizontally, with 10% margin on top.
    '''
    font = cv2.FONT_HERSHEY_DUPLEX
    title_size = cv2.getTextSize(title, font, 1, 2)[0]

    canvas = cv2.putText(
        canvas, title,
        (int((canvas.shape[1]-title_size[0])/2), int(canvas.shape[0] * 0.1)),
        font, 1, (255, 255, 255), 2
    )

    return canvas
