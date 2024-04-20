# our controller is max 500kHz
# motor is 1.8 degrees per step, we set the pins to
# this class counts on the pulses/rev to be on 200 setting (see manual fot CL57T stepper controller)

from machine import Pin
from time import sleep


# TODO see if we are using the enable pin and implement it
class Stepper:
    def __init__(self, stepPin, dirPin, enablePin, sleepTime=0.005):
        lyst = []
        for p in (stepPin, dirPin, enablePin):
            if not isinstance(p, Pin):
                p = Pin(p, value=0, mode=Pin.OUT)
            lyst.append(p)
        self.stepPin = lyst[0]
        self.dirPin = lyst[1]
        self.enablePin = lyst[2]
        self.direction = 0  # will be 0 for CW or 1 for CCW
        self.currentPos = 0  # will be from -FULL_TURN to FULL_TURN
        self.sleepTime = sleepTime  # determines wait time in between pulses, also determines pulse frequency
        self.FULL_TURN = 400  # two revolutions, TODO change this to be the right number for tug wheels

    def turn(self, value):
        """value from -100 to 100, 0 being going strait"""
        stepToPos = value * self.FULL_TURN // 100
        if self.currentPos == stepToPos:  # don't turn the wheels anymore
            return
        elif stepToPos > self.currentPos and self.direction == 1:
            self.reverseDir()
        elif stepToPos < self.currentPos and self.direction == 0:
            self.reverseDir()
        # get how many steps to take
        stepsToTake = 0
        if (self.currentPos > 0 and stepToPos > 0) or (
            self.currentPos < 0 and stepToPos < 0
        ):  # if signs are the same
            stepsToTake = abs(abs(stepToPos) - abs(self.currentPos))
        else:  # signs are different or one number is 0
            stepsToTake = abs(stepToPos) + abs(self.currentPos)
        # if abs(self.currentPos + stepToPos) > self.FULL_TURN:
        #     stepToPos -= self.currentPos + stepToPos - self.FULL_TURN
        while stepsToTake > 0:
            self.stepOnce()
            stepsToTake -= 1
        # set new position
        self.currentPos = stepToPos

    def stepOnce(self):
        self.stepPin.value(1)
        sleep(self.sleepTime)
        self.stepPin.value(0)
        sleep(self.sleepTime)

    def reverseDir(self):
        if self.direction == 1:
            self.dirPin.value(0)
            self.direction = 0
        else:  # value == 0
            self.dirPin.value(1)
            self.direction = 1

    # def turnOff(self):
