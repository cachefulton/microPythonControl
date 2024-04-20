# this file focuses on BLDC motor control and the stepper class takes care of the steering
# TODO turn off all items before battery power gets too low.

import select
import sys
from machine import Pin
from time import sleep
from stepper import Stepper
from dcMotorControl import BLDC
from linearActuator import LinearActuator
from solenoid import Solenoid


class Controller:
    def __init__(self, numChannels):
        self.channelList = [0] * numChannels
        # self.changedList = [0] * numChannels

    def parseStringInput(self, str):
        """
        adds string values to channelList separated by spaces
        returns true at least one item has changed
        false if none have changed
        """
        hasChanged = False  # if any controller values have changed
        toFloat = ""
        ind = 0
        for char in str:
            if char == " " or char == "\n":
                temp = float(
                    toFloat
                )  # need to use float because all numbers from controller are floats
                if self.channelList[ind] != temp:
                    hasChanged = True
                    self.channelList[ind] = temp
                ind += 1
                toFloat = ""
            else:
                toFloat += char
        return hasChanged


def setWheelsStrait():
    # if doing this with a switch:
    # turn one direction until switch is on
    # or turn the other direction if switch is off
    return


# TODO make a reset function to make sure all pins and values get reset
# this is because pico will maintain last pin value if power is still being fed to it
# which it will be because the jetson will continue giving power through usb


def main():
    # Set up the poll object
    pollObj = select.poll()
    pollObj.register(sys.stdin, select.POLLIN)
    led = Pin("LED", Pin.OUT)
    led.value(1)

    # channel layout
    # 0 - turnLeftRight (-100 to 100)
    # 1 - turnForwardBack (0 to -100, will brake the amount passed, 0 no brake, -100 full brake)
    # 2 - throttle (0 to 100)
    # 3 - throttleLeftRight
    # 4 - dialLeft
    # 5 - dialRight
    # 6 - reverseSwitch (1 or 0, 0 is actually forward)
    # 7 - switchMidLeft
    # 8 - switchMidRight
    # 9 - switchRight (1 or 0, 0 is brake on, 1 is brake off)
    control = Controller(10)  # number of channels

    # initialize brakes
    # brake overrides throttle, if any breaks
    lnAct = LinearActuator(18, 19, 20, 21)

    # initialize motor class
    bldc = BLDC(12, 15, 13)

    # initialize stepper class
    stepper = Stepper(6, 7, 8)
    # TODO set wheel position to 0 after startup (probably from main control), can do this by using an optical or electrical switch

    solAttach = Solenoid(27)
    solLazySusan = Solenoid(22)

    sleep(0.5)  # wait a little to make sure everything is ready

    # tell computer that pico is ready
    # sys.stdout.write("ready\n")

    # turn values are -100-100, throttle/dial values are from 0-100 unless it's a switch, switches are 0 or 1
    # Loop indefinitely
    while True:
        # Wait for input on stdin
        pollResults = pollObj.poll(
            -1
        )  # the '1' is how long it will wait for message before looping again (in microseconds)
        if pollResults:
            # read data coming from PC. It needs to have a '\n' at of data end to signal readline
            channels = sys.stdin.readline()
            hasChanged = control.parseStringInput(channels)

            if hasChanged:
                stepper.controlTurn(control.channelList[0])
                solAttach.setPin(control.channelList[7])

                # we want brakes to default to on so a 0 input will be on and 1 input will be off
                # if e brake are on we don't want the throttle on
                if not control.channelList[9]:
                    bldc.setDrive(0)
                    lnAct.setBrake(100)
                # anything less then -10, to give a little leeway
                elif control.channelList[1] <= -15:
                    bldc.setDrive(0)
                    lnAct.setBrake(abs(int(control.channelList[1])))
                # if no brakes whatsoever, control throttle like usual
                else:
                    # make sure brake is off
                    # bldc.turnOffLowLevelBrake()  # TODO temp
                    lnAct.setBrake(0)
                    # set drive
                    # the control sends 0 default and that is the direction we want as forward
                    # the reverse pin needs to be on for forward so switch 0 to 1 and 1 to 0
                    bldc.reverseDirection(not control.channelList[6])
                    bldc.setDrive(control.channelList[2])
            # else:
            # because I don't send unchanged data, and the stepper works with a queue,
            # it needs to know to take the next steps in the queue
            # stepper.takeSteps()
            # TODO if inactive, shut down devices and go to sleep (use enable pins)
            # Write the data back to pc
            # sys.stdout.write(channels)

        else:
            # do something if no message received (like feed a watchdog timer)
            continue


if __name__ == "__main__":
    main()
