from codrone_edu.drone import Drone
import time


class TDrone(Drone):
    """
    A class to implement a context manager for Robolink's CoDrone EDU platform.
    Now automatically pairs and disconnects when entering and exiting the `with` context,
    increasing runtime safety and ease of development and testing.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __enter__(self):
        # Pair the drone
        self.pair()
        time.sleep(0.2)
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.land()
        self.close()

        # Print Errors
        if exc_value is not None:
            print(exc_type, exc_value, exc_tb, sep='\n')

    def __del__(self):
        # Overload to prevent close from being called twice.
        pass

    def fire_start(self):
        """
        Convenient method to block until key-input is entered.
        """
        start_key = 's'
        self.takeoff()
        self.hover()
        ready = False
        self.set_drone_LED(0, 0, 255, 100)
        while not ready:
            key = input(f"Press {start_key} to begin: ")
            if key.lower() == start_key:
                print("Beginning Flight.")
                ready = True
                self.set_drone_LED(0, 255, 0, 100)
                time.sleep(0.1)
