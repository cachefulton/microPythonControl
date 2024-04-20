lastPos = 0
MAX_DELAY = 100


def setBrake(position):
    global lastPos, MAX_DELAY
    """
    takes a number between 0 - 100,
    0 = no brakes, 100 = full brakes,
    converts position to delay
    """

    tempPos = abs(lastPos - position)
    # delay = round(tempPos * MAX_DELAY / 100)
    if lastPos > position:
        # retract(delay)
        print("reverse", tempPos)
        lastPos = position
    elif lastPos < position:
        # extend(delay)
        print("extend", tempPos)
        lastPos = position


# setBrake(1)
# setBrake(5)
# setBrake(8)
# setBrake(11)
setBrake(100)
setBrake(100)
setBrake(99)
setBrake(99)
setBrake(0)
setBrake(44)
setBrake(44)
setBrake(43)
# setBrake(1)
# setBrake(2)
# setBrake(14)
# setBrake(0)
# setBrake(0.1)
# setBrake(0.9)
# setBrake(1.4)
# setBrake(2.5)
