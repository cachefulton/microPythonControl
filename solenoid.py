from machine import Pin


class Solenoid:
    def __init__(self, pin1):
        """
        pin1 turns on and off to control solenoid
        """
        if not isinstance(pin1, Pin):
            pin1 = Pin(pin1, value=0, mode=Pin.OUT)
        self.pin1 = pin1

    def setPin(self, onOrOff):
        """
        takes 0 or 1 to turn pin1 on or off
        """
        self.pin1(onOrOff)
