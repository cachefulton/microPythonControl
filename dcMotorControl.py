from machine import Pin, PWM
from time import sleep


# read that brushless dc motors should not have less than 5000 hz
# drive reverse only has one pin because we are making the motors turn the same direction
class BLDC:
    def __init__(self, throttlePin, lowLevelBrakePin, reversePin, freq=7000):
        lyst = []
        for p in (throttlePin, lowLevelBrakePin, reversePin):
            if not isinstance(p, Pin):
                p = Pin(p, value=0, mode=Pin.OUT)
            lyst.append(p)
        # self.throttlePin = lyst[0]
        self.PWMThrottle = PWM(lyst[0], freq=freq, duty_u16=0)
        self.lowLevelBrakePin = lyst[1]
        self.reversePin = lyst[2]
        self.freq = freq
        # default direction forward is reverse pin on
        self.direction = 1
        self.reversePin.value(1)
        sleep(0.5)

    def checkWheelStopped(self):
        """
        relies on reverseDirection
        sets speed to 0 and sleeps to let the motors stop
        """
        # TODO need hall sensor data to actually check if the motors are stopped
        self.PWMThrottle.duty_u16(0)
        sleep(0.75)

    def reverseDirection(self, value):
        """
        checks if wheels are stopped
        uses switch value, 0 or 1, to set direction
        """
        if value == self.direction:
            return
        self.direction = value
        # should be able to use switch value to turn on and off reverse switches
        self.checkWheelStopped()
        # reverse the direction by turning on or off another pin
        self.reversePin.value(value)
        sleep(0.25)  # sleep to make sure motor pin has reversed

    def setDrive(self, value):
        """
        relies on parseChannels function
        sets motors to different duty cycles for PWM
        throttle is from 0-100
        """
        self.PWMThrottle.duty_u16(
            int(value * 65535 / 100)
        )  # duty_u16 only takes value 0-65535

    def turnOnLowLevelBrake(self):
        self.lowLevelBrakePin.value(1)

    def turnOffLowLevelBrake(self):
        self.lowLevelBrakePin.value(0)
