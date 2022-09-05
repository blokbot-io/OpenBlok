''' Performs pre-checks to ensure the system is ready to run OpenBlok '''

import pkg_resources

import cv2

# --------------------------- Validate Requirements -------------------------- #


def validate_requirements():
    '''.
    Validates all requirements are installed.
    '''
    with open('requirements.txt', 'r', encoding="UTF-8") as requirements_file:
        requirements = requirements_file.read().splitlines()

    try:
        pkg_resources.require(requirements)
    except pkg_resources.DistributionNotFound as err:
        print(err)
        return False
    return True

# ----------------------------- Peripheral Check ----------------------------- #


def peripheral_check():
    '''.
    Performs a check that the following peripherals are connected and available:
    - USB Camera
    '''
    cap = cv2.VideoCapture(0)
    if cap is None or not cap.isOpened():
        print("USB Camera not connected")
        return False
    cap.release()
    return True
