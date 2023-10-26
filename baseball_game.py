#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""baseball_game:

A Series of functions to assist with the development of a drone baseball
emulation program.

Author: Terrance Williams
"""


# noinspection PyUnresolvedReferences
import time
import logging
from pathlib import Path
from codrone_edu.drone import *
from tjdrone import TDrone


# %% CONSTANTS
PITCH_POWER, ROLL_POWER, THROTTLE_POWER = 15, 15, -25  # power and directions: forward, right, and down
MOVE_VELOCITY = 0.5  # (m/s) MAX: 2.0 m/s
MOVE_TIME = 0.1
SLEEP_TIME = 1.5
COLOR_DETECT_THRESH = 50
SWITCH_DIST_THRESH: float = 20.  # (cm); Relative height difference that denotes a change from or to a base.
MIN_RELATIVE_HEIGHT, MAX_RELATIVE_HEIGHT = 15, 20  # (cm)
HEIGHT_SWITCHES = 2  # Number of times relative height must switch (i.e. exceed difference threshold)
TOTAL_BASES: int = 4
BTMRANGE_SENSOR_UNIT = 'cm'
COLOR_DETECT_ATTEMPTS = 20

# Notes
C4 = Note.C4
E4 = Note.E4
G4 = Note.G4
C5 = Note.C5
REST = Note.Mute
NOTE_DURATION = 250  # (ms) 6/8 time at 120 BPM

# %% Mappings
HOME = 0
BASE_1 = 1
BASE_2 = 2
BASE_3 = 3
# Base Color mapping [color: (base_num, color_rgb)]
base_color_mappings = {
    'green': (HOME, (0, 255, 0)),
    'red': (BASE_1, (255, 0, 0)),
    'yellow': (BASE_2, (255, 255, 0)),
    'blue': (BASE_3, (0, 0, 255))
}
base_number_mappings = {
    HOME: 'Home',
    BASE_1: 'First',
    BASE_2: 'Second',
    BASE_3: 'Third'
}
hit_mappings = {
    'miss': 0,
    'single': 1,
    'double': 2,
    'triple': 3,
    'home run': 4
}
base_waypoints = {}

# %% Logging
log_path = Path() / 'logs'
if not log_path.exists():
    log_path.mkdir()

log_index = len([x for x in log_path.iterdir()])
logfile = log_path / f'baseball_{log_index:02d}.log'
logging.basicConfig(filename=logfile, encoding='utf-8', level=logging.DEBUG)


def low_hover(drone: Drone,
              min_height=MIN_RELATIVE_HEIGHT,
              max_height=MAX_RELATIVE_HEIGHT) -> float:
    """Hover the drone within some relative height range"""
    drone.takeoff()
    drone.hover(SLEEP_TIME)
    drone.set_throttle(THROTTLE_POWER)

    curr_dist = 0
    while not min_height < curr_dist < max_height:
        drone.move(MOVE_TIME)
        curr_dist = drone.get_bottom_range(unit=BTMRANGE_SENSOR_UNIT)
        time.sleep(0.01)
    else:
        return curr_dist


# noinspection PyPep8Naming
def calibrate_bases(drone: Drone) -> bool:
    """Sets waypoints for each base"""

    # noinspection PyUnusedLocal
    ret = False
    color_path = Path('../color_data')

    # Load color classifier
    if not color_path.is_dir():
        print("Could not find color_data directory. Using defaults")
        drone.load_classifier()
    else:
        drone.load_classifier(dataset=color_path)

    # Set each base's waypoint starting with first base and ending with Home
    """for i in range(TOTAL_BASES):
        base_to_calibrate = (i + 1) % TOTAL_BASES
        logging.info(f'[calibrate_bases] Calibrating Base {base_number_mappings[base_to_calibrate]}')
        print(f'[calibrate_bases] Place Drone on {base_number_mappings[base_to_calibrate]} Base.')

        consec_detect = 0
        while consec_detect < COLOR_DETECT_THRESH:
            color = drone.predict_colors(drone.get_color_data())
            # print(color)
            frnt_clr, back_clr = color
            if frnt_clr == back_clr and frnt_clr in base_color_mappings:
                current_base, LED_color = base_color_mappings[frnt_clr]
                drone.set_drone_LED(*LED_color, 100)
                if current_base == base_to_calibrate:
                    consec_detect += 1
                    print(f'{COLOR_DETECT_THRESH - consec_detect}',
                          end=' ')
                else:
                    print('\r', end="")
                    consec_detect = 0
            else:
                print('\r', end="")
                consec_detect = 0
        else:
            # Add waypoint to mapping dict
            _ = low_hover(drone)
            drone.set_waypoint()
            drone.land()
            base_waypoints[base_to_calibrate] = drone.waypoint_data[i]
            print('')
            # time.sleep(SLEEP_TIME)
    else:
        ret = True"""
    ret = True
    return ret


def play_ball(drone: Drone):

    """
    Perform any required drone setup.
    Waits until drone is on the HOME plate, plays the start song, and then
    awaits user input
    """

    # Print base-color associations
    message = ("Welcome to Drone Baseball!\nBefore we begin, let's calibrate"
               "the bases.\nHere are the current color associations:")
    print(message)
    logging.info("Current Base-Color Associations")
    for color in base_color_mappings:
        base_num = base_color_mappings[color][0]
        assoc_base = base_number_mappings[base_num]
        print(f'{color.title()}:\t{assoc_base}')
        logging.info(f'{color.title()}:\t{assoc_base}')

    assert calibrate_bases(drone)

    # Play Baseball Song
    """drone.drone_buzzer(C4, NOTE_DURATION)
    drone.drone_buzzer(E4, NOTE_DURATION)
    drone.drone_buzzer(G4, NOTE_DURATION)
    drone.drone_buzzer(C5, NOTE_DURATION // 2)
    drone.drone_buzzer(REST, NOTE_DURATION)
    drone.drone_buzzer(G4, NOTE_DURATION)
    drone.drone_buzzer(C5, 3 * NOTE_DURATION)"""

    print("\nPlay Ball!\n")
    time.sleep(SLEEP_TIME)

    for key in base_waypoints:
        print(base_waypoints[key])
    await_input(drone)

    logging.info("User Exit.")


def await_input(drone: Drone) -> None:
    quit_signal = 'q'
    done = False
    current_base = HOME

    while not done:
        input_val = input("Insert a Hit Value: ").lower()
        if input_val == quit_signal:
            print("[INFO] EXITING program.")
            done = True

        elif input_val in hit_mappings:
            num = hit_mappings[input_val]
            current_base = move_bases(current_base, num, drone)
        elif input_val in [str(i) for i in range(5)]:
            num = int(input_val)
            current_base = move_bases(current_base, num, drone)
        else:
            print("Insert a hit value (miss, single, double, triple, or home run) or",
                  " the number of bases to run (0 to 4).\n", "Enter 'q' to quit.\n", sep='')


def move_bases(current_base: int, num_bases: int, drone: Drone):
    """Performs a series of base movements"""
    # Input checks
    try:
        if current_base < HOME or num_bases < 0:
            raise ValueError("Current Base and number of bases to run must be non-negative.")
        if current_base > BASE_3:
            logging.critical(f'Input base {current_base} is outside bounds.')
            raise ValueError("Current Base is limited from 0 to 3 (inclusive).")
    except TypeError:
        print("Current Base and number of bases to run must be integers.")
        raise
    # Ensure integer inputs (floors any non-int value)
    current_base, num_bases = int(current_base), int(num_bases)

    # Trivial condition
    if num_bases == 0:
        print("[INFO] Drone does not move.")
        logging.info("[move bases] Drone doesn't move.")
        return current_base

    # Check if provided number of bases to run result in a full run (back to HOME).
    if current_base + num_bases >= TOTAL_BASES:
        num_bases = TOTAL_BASES - current_base

    print(f'[move_bases] (Current Base, Target Base): ({current_base}, '
          f'{(current_base + num_bases) % TOTAL_BASES})')
    logging.info(f'[move_bases] (Current Base, Target Base): ({current_base}, '
                 f'{(current_base + num_bases) % TOTAL_BASES})')
    # Move to the bases
    for i in range(num_bases, 0, -1):
        current_base = move(current_base, drone)
    else:
        return current_base


# noinspection PyPep8Naming
def move(current_base: int, drone: Drone) -> int:
    """Moves from current base to next base"""
    dist_switch = 0

    # Ensure that the drone is on the proper current base.
    test_color = drone.predict_colors(drone.get_color_data())
    assert test_color[0] == test_color[1]
    test_base, _ = base_color_mappings[test_color[0]]
    try:
        assert test_base == current_base
    except AssertionError:
        print("Program current base and Real-World current base are misaligned.")
        print(f'Program Base: {current_base}\nReal Base: {test_base}')
        raise

    target_base = (current_base + 1) % TOTAL_BASES
    logging.info(f'[move] Moving from {current_base} to {target_base}')
    print(f'[move] Moving from {current_base} to {target_base}')

    curr_dist = low_hover(drone)
    # reset parameters
    drone.hover(SLEEP_TIME)
    # time.sleep(SLEEP_TIME)
    logging.debug(f'Initial Bottom Range Value {BTMRANGE_SENSOR_UNIT}: {curr_dist}')

    # Set new movement params
    '''
    Movement logic. ASSUMES ONLY TRANSLATIONAL MOVEMENT (for now).
    HOME: move forward and to the right at a 45 deg. angle to Base 1
    Base 1: Move forward and to the left at a 45 deg. angle to Base 2
    Base 2: Move backwards and to the left ... to Base 3
    Base 3: Move backwards and to the right ... to HOME
    '''
    if current_base == HOME:
        drone.set_pitch(PITCH_POWER)
        # drone.set_roll(ROLL_POWER)
    elif current_base == BASE_1:
        # drone.set_pitch(PITCH_POWER)
        drone.set_roll(-ROLL_POWER)
    elif current_base == BASE_2:
        drone.set_pitch(-PITCH_POWER)
        # drone.set_roll(-ROLL_POWER)
    elif current_base == BASE_3:
        # drone.set_pitch(-PITCH_POWER)
        drone.set_roll(ROLL_POWER)
    else:
        # If somehow the current_base is invalid.
        raise ValueError(f"Invalid current base value: {current_base}")

    # Move until the drone reaches another base (two substantial
    # changes in relative height)
    while dist_switch < HEIGHT_SWITCHES:
        drone.move(MOVE_TIME)
        # time.sleep(MOVE_TIME)
        next_dist = drone.get_bottom_range(unit=BTMRANGE_SENSOR_UNIT)
        logging.debug(f'[move] Bottom-Range Reading: {next_dist}')
        print(f'[move] Bottom-Range Reading: {next_dist}')
        if abs(next_dist - curr_dist) >= SWITCH_DIST_THRESH and curr_dist > 0:
            dist_switch += 1
            logging.info(f'[move] Relative Height switch no. {dist_switch} from {curr_dist} to {next_dist}')
            print(f'[move] Relative Height switch no. {dist_switch} from {curr_dist} to {next_dist}')
            curr_dist = next_dist
    else:
        logging.info('Distance-switching trips met.')
        print('Distance-switching trips met.')

    # Land the drone and detect color
    drone.hover(MOVE_TIME)
    print("[INFO] Adjusting position...")

    # Movement Adjustment
    # drone.goto_waypoint(base_waypoints[target_base], MOVE_VELOCITY)
    drone.land()
    while drone.get_bottom_range(unit=BTMRANGE_SENSOR_UNIT) > 0:
        time.sleep(SLEEP_TIME/4)

    # Detect Base based on color
    for i in range(COLOR_DETECT_ATTEMPTS):
        colors_detected = drone.predict_colors(drone.get_color_data())
        if colors_detected[0] != colors_detected[1]:
            logging.debug(f"[move] Color-Detection {i}: Color values differ {colors_detected}.")
            continue
        if colors_detected[0] in base_color_mappings:
            current_base, LED_color = base_color_mappings[colors_detected[0]]
            logging.info(f'[move] Detected {colors_detected[0]} associated with Base {current_base}')
            break
        time.sleep(SLEEP_TIME/10)
    else:
        # noinspection PyUnboundLocalVariable
        logging.critical(f"[move] Detected color {colors_detected} is not one of the colors assoc. with a base.")
        raise ValueError(f"[move] Detected color {colors_detected} is not one of the colors assoc. with a base.")

    # Change LED Color
    drone.set_drone_LED(*LED_color, 100)
    if current_base != target_base:
        logging.critical('Drone landed on incorrect base.')
        raise ValueError('[ERROR]: Drone landed on incorrect base.')
    else:
        logging.info("[move] Success.")
        print("[move] Success.")
        return current_base


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    with TDrone() as t_drone:
        t_drone.set_trim(0, 0)
        play_ball(t_drone)
