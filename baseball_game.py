#! /usr/bin/env python3
# -*- coding: utf-8 -*-


# noinspection PyUnresolvedReferences
import time
import logging
from pathlib import Path
from codrone_edu.drone import *
from tjdrone import TDrone

"""baseball_game:

A Series of functions to assist with the development of a drone baseball
emulation program.

Author: Terrance Williams
"""

# %% CONSTANTS
MOVE_TIME = 0.1
SLEEP_TIME = 1.5
COLOR_DETECT_THRESH = 50
SWITCH_DIST_THRESH: float = 20.  # (cm); Relative height difference that denotes a change from or to a base.
# BASE_RELATIVE_HEIGHT =
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
# Base mapping [color: (base_num, color_rgb)]
base_mappings = {'green': (0, (0, 255, 0)),
                 'red': (1, (255, 0, 0)),
                 'yellow': (2, (255, 255, 0)),
                 'blue': (3, (0, 0, 255))}
hit_mappings = {'miss': 0,
                'single': 1,
                'double': 2,
                'triple': 3,
                'home run': 4}

# %% Logging

log_path = Path() / 'logs'
if not log_path.exists():
    log_path.mkdir()

log_index = len([x for x in log_path.iterdir()])
logfile = log_path / f'baseball_{log_index:02d}.log'
logging.basicConfig(filename=logfile, encoding='utf-8', level=logging.DEBUG)


# noinspection PyPep8Naming
def play_ball(drone: Drone):

    """
    Perform any required drone setup.
    Waits until drone is on the HOME plate, plays the start song, and then
    awaits user input
    """
    color_path = Path('../color_data')
    # Load color classifier
    if not color_path.is_dir():
        print("Could not find color_data directory. Using defaults")
        drone.load_classifier()
    else:
        drone.load_classifier(dataset=color_path)

    # Check current base
    consec_detect = 0
    while consec_detect < COLOR_DETECT_THRESH:
        color = drone.predict_colors(drone.get_color_data())
        print(color)
        frnt_clr, back_clr = color
        if frnt_clr == back_clr and frnt_clr in base_mappings:
            current_base, LED_color = base_mappings[frnt_clr]
            drone.set_drone_LED(*LED_color, 100)
            if current_base == 0:
                consec_detect += 1
        else:
            consec_detect = 0

    # Play Baseball Song
    drone.drone_buzzer(C4, NOTE_DURATION)
    drone.drone_buzzer(E4, NOTE_DURATION)
    drone.drone_buzzer(G4, NOTE_DURATION)
    drone.drone_buzzer(C5, NOTE_DURATION // 2)
    drone.drone_buzzer(REST, NOTE_DURATION)
    drone.drone_buzzer(G4, NOTE_DURATION)
    drone.drone_buzzer(C5, 3 * NOTE_DURATION)

    print("Play Ball!\n")
    time.sleep(SLEEP_TIME)
    await_input(drone)

    logging.info("User Exit.")


def await_input(drone: Drone) -> None:
    quit_signal = 'q'
    done = False
    current_base = 0  # Begin at HOME

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
        if current_base < 0 or num_bases < 0:
            raise ValueError("Current Base and number of bases to run must be non-negative.")
        if current_base > 3:
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
    pitch, roll = 30, 20  # power and directions: forward and right
    dist_switch = 0

    # Ensure that the drone is on the proper current base.
    test_color = drone.predict_colors(drone.get_color_data())
    assert test_color[0] == test_color[1]
    test_base, _ = base_mappings[test_color[0]]
    try:
        assert test_base == current_base
    except AssertionError:
        print("Program current base and Real-World current base are misaligned.")
        print(f'Program Base: {current_base}\nReal Base: {test_base}')
        raise

    '''
        Movement logic. ASSUMES ONLY TRANSLATIONAL MOVEMENT (for now).
        HOME: move forward and to the right at a 45 deg. angle to Base 1
        Base 1: Move forward and to the left at a 45 deg. angle to Base 2
        Base 2: Move backwards and to the left ... to Base 3
        Base 3: Move backwards and to the right ... to HOME
    '''
    if current_base == 0:
        drone.set_pitch(pitch)
        drone.set_roll(roll)
    elif current_base == 1:
        drone.set_pitch(pitch)
        drone.set_roll(-roll)
    elif current_base == 2:
        drone.set_pitch(-pitch)
        drone.set_roll(-roll)
    elif current_base == 3:
        drone.set_pitch(-pitch)
        drone.set_roll(roll)
    else:
        # If somehow the current_base is invalid.
        raise ValueError(f"Invalid current base value: {current_base}")

    target_base = (current_base + 1) % TOTAL_BASES
    logging.info(f'[move] Moving from {current_base} to {target_base}')
    print(f'[move] Moving from {current_base} to {target_base}')
    """drone.takeoff()
    drone.hover(1)"""
    time.sleep(SLEEP_TIME)
    curr_dist = 0
    while not curr_dist > 0:
        curr_dist = drone.get_bottom_range(unit=BTMRANGE_SENSOR_UNIT)
        time.sleep(0.1)
    logging.debug(f'Initial Bottom Range Value {BTMRANGE_SENSOR_UNIT}: {curr_dist}')

    # Move until the drone reaches another base (two huge rel. height changes)
    while not dist_switch > 1:
        # drone.move(MOVE_TIME)
        time.sleep(MOVE_TIME)
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
    """drone.hover(MOVE_TIME)
    drone.land()"""
    print("[INFO] Landing.")
    time.sleep(2 * SLEEP_TIME)

    for i in range(COLOR_DETECT_ATTEMPTS):
        colors_detected = drone.predict_colors(drone.get_color_data())
        if colors_detected[0] != colors_detected[1]:
            logging.debug(f"[move] Color-Detection {i}: Color values differ {colors_detected}.")
            continue
        if colors_detected[0] in base_mappings:
            current_base, LED_color = base_mappings[colors_detected[0]]
            logging.info(f'[move] Detected {colors_detected[0]} associated with Base {current_base}')
            break
        time.sleep(SLEEP_TIME/10)
    else:
        # noinspection PyUnboundLocalVariable
        print(f"[move] Detected color {colors_detected} is not one of the colors assoc. with a base.")
        logging.critical(f"[move] Detected color {colors_detected} is not one of the colors assoc. with a base.")
        raise

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
    # logging.getLogger().setLevel(logging.INFO)
    with TDrone() as t_drone:
        play_ball(t_drone)
