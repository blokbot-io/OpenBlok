''' Module | serial '''

import time
from decimal import Decimal

import config
import serial

arduino = serial.Serial(port='/dev/ttyACM0', baudrate=9600, timeout=.3)

# try:
#     arduino = serial.Serial(port='/dev/ttyACM0', baudrate=9600, timeout=.3)
# except serial.serialutil.SerialException as err:
#     print(f"Error starting serial connection: {err}")

# config.part_velocity = None  # in/s origional .635 then 0.66
config.part_velocity = Decimal(0.66)


TRAVEL_DISTANCE = 40  # in

# ---------------------------------------------------------------------------- #
#                               Position Schedule                              #
# ---------------------------------------------------------------------------- #
# bin_number | The bin location that matches the expected part number.
# drop_time | The time that the part should be falling into the bin.
# bin_time | The time that the carousel should be at the bin position.
POSITION_SCHEDULE = []  # Array or [bin_number, drop_time, bin_time, position, confidence]
BIN_ASSIGNMENT = []

# -------------------------------- Positioning -------------------------------- #


def update_position_schedule(capture_time, position, part_number, confidence):
    '''
    Updates the schedule of positions where the carousel should be at.
    Capture Time - The timestamp for when the frame was captured.
    Position - Position of the part in the captured frame.
    Part Number - The predicted part number.
    Confidence - The confidence of the prediction.
    '''
    print("--- Updating Bin Position Schedule ---")
    print(f"Capture Time: {capture_time} | Position: {position}")
    print(f"Part Number: {part_number} | Confidence: {confidence}")
    print(f"Current timestamp: {time.time()}")

    # Assign the part to a bin if it is not already assigned.
    if str(part_number) not in BIN_ASSIGNMENT:
        BIN_ASSIGNMENT.append(str(part_number))

    # If part number exceeds the number of bins available, place it in the last bin.
    if BIN_ASSIGNMENT.index(str(part_number)) > 35:
        bin_number = 36
    else:
        bin_number = BIN_ASSIGNMENT.index(str(part_number))+1

    print(f"Bin Number: {bin_number}")

    relative_position = (position-config.AruCo_center_y)/config.AruCo_px_per_inch
    remaining_distance = TRAVEL_DISTANCE - relative_position  # Remaining distance to the bin

    if config.part_velocity is None:
        config.part_velocity = True
        drop_time = time.time()
    elif config.part_velocity is True:
        config.part_velocity = [capture_time, relative_position]
        drop_time = time.time()
    elif isinstance(config.part_velocity, list):
        config.part_velocity = abs(
            Decimal(config.part_velocity[1] - relative_position)
        ) / (capture_time - config.part_velocity[0])

        print(f"-----> Part Velocity: {config.part_velocity} <-----")
        drop_time = time.time()
    else:

        time_left_to_drop = Decimal(remaining_distance) / config.part_velocity  # in seconds
        drop_time = capture_time + Decimal(time_left_to_drop)            # in seconds

    if len(POSITION_SCHEDULE) == 0:
        bin_time = time.time()
    else:
        previous_queue_number = len(POSITION_SCHEDULE)-1
        leading_part = POSITION_SCHEDULE[previous_queue_number]

        time_difference = Decimal(drop_time) - Decimal(leading_part[1])

        # Checks if the leading and current part are the same.
        print(f"Time Difference | {time_difference}s")
        if 0 < time_difference < 15:
            if Decimal(confidence) > Decimal(leading_part[4]):
                leading_part[0] = bin_number
                print("Updated position schedule with better confidence.")

            print("Did not update position schedule with better confidence.")
            return POSITION_SCHEDULE

        # Moves bin into position between the drop time of the leading and current part.
        bin_time = Decimal(drop_time) - (Decimal(time_difference)*Decimal(.7))

    POSITION_SCHEDULE.append([
        bin_number,
        Decimal(drop_time), Decimal(bin_time),
        relative_position, confidence
    ])

    print("--- Bin Schedule Updated ---")
    for bin_position in POSITION_SCHEDULE:
        print(f"Bin: {bin_position[0]} Drop Time: {bin_position[1]} Bin Time: {bin_position[2]}")

    return POSITION_SCHEDULE


def carousel_position():
    '''
    To be ran in a thread.
    Continuously updates the position of the carousel.
    '''
    current_bin = None
    while True:
        if POSITION_SCHEDULE is not None and len(POSITION_SCHEDULE) > 0:
            bin_number = POSITION_SCHEDULE[0][0]
            drop_time = POSITION_SCHEDULE[0][1]
            bin_time = POSITION_SCHEDULE[0][2]

            # Move the carousel to the bin position if the time is current or passed.
            if bin_time <= Decimal(time.time()) and current_bin != bin_number:
                write_serial(f"{bin_number}")
                print(f"Carousel is at bin {bin_number}")
                current_bin = bin_number

            if drop_time <= time.time():
                print(f"Part {POSITION_SCHEDULE[0][0]} is falling into bin {bin_number}")
                POSITION_SCHEDULE.pop(0)
        time.sleep(3)


# --------------------------- Serial Communication --------------------------- #
def serial_listener():
    '''
    Reads data from the serial port.
    '''
    print("Serial listener started.")
    while True:
        while arduino.in_waiting > 0:
            print(f"Serial message: {arduino.readline()}")

        time.sleep(1)


def write_serial(data):
    '''
    Writes and reads data from the arduino.
    '''
    arduino.write(bytes(data, 'utf-8'))
    time.sleep(0.5)
    data = arduino.readline()
    print(data)
