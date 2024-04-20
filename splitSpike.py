from array import array
import sys

# from time import sleep
import asyncio


stepsAndDirArr = array("H", [0, 1])  # arr
direction = 0  # will be 0 for CW or 1 for CCW
currentPos = 0  # will be from -FULL_TURN to FULL_TURN
lastStepToPos = 0
# leftOver = 0
# splitNum = 0
stepQueue = []  # will remake this about every pass
FULL_TURN = 400
currentStep = 0  # total sum of stepArr


def makeQueue(stepTo):
    global currentPos, splitNum, currentStep, stepArr
    # if step is big in one direction up step count
    # get how many steps to take
    if (currentPos > 0 and stepTo > 0) or (
        currentPos < 0 and stepTo < 0
    ):  # if signs are the same
        currentStep = abs(abs(stepTo) - abs(currentPos))
        # if inside
    else:  # signs are different or one number is 0
        currentStep = abs(stepTo) + abs(currentPos)
    stepArr = []
    leftOver = currentStep % 4
    splitNum = currentStep // 4

    stepArr.append(leftOver + splitNum)
    # I need to know these leftOver + splitNum
    if splitNum > 0:
        stepArr.append(splitNum)
        stepArr.append(splitNum)
        stepArr.append(splitNum)

    # return lyst


def checkList(value):
    global currentStep, stepArr, lastStepToPos, stepsAndDirArr, currentPos
    stepToPos = value * FULL_TURN // 100
    # if stepToPos has changed at all, remake queue and make sure direction is correct
    # if lastStepToPos == stepToPos:
    #     if stepArr:
    #         stepArr.pop(0)
    if currentPos == stepToPos:  # don't turn the wheels anymore

        return
    if stepToPos > currentPos and direction == 1:
        reverseDir()
    elif stepToPos < currentPos and direction == 0:
        reverseDir()

    # empty queue, and remake it in right direction
    if lastStepToPos != stepToPos:
        makeQueue(stepToPos)
    steps = stepArr.pop(0)
    stepsAndDirArr[0] = steps
    stepsAndDirArr[1] = direction
    # stateMachine.put(stepsAndDirArr)
    print(stepsAndDirArr)
    # TODO check fifo and if it's full just skip?
    lastStepToPos = stepToPos
    currentStep -= steps
    if direction:
        currentPos -= steps
    else:
        currentPos += steps


def turn(value):
    """value from -100 to 100, 0 being going strait"""
    global FULL_TURN, currentPos, direction, stepArr, currentStep
    stepToPos = value * FULL_TURN // 100
    if currentPos == stepToPos:  # don't turn the wheels anymore
        return
    elif stepToPos > currentPos and direction == 1:
        reverseDir()
    elif stepToPos < currentPos and direction == 0:
        reverseDir()
    # get how many steps to take
    if (currentPos > 0 and stepToPos > 0) or (
        currentPos < 0 and stepToPos < 0
    ):  # if signs are the same
        currentStep = abs(abs(stepToPos) - abs(currentPos))
    else:  # signs are different or one number is 0
        currentStep = abs(stepToPos) + abs(currentPos)
    stepArr = splitStep(currentStep)
    smallStep = stepArr.pop(0)  # take the step

    currentStep -= smallStep
    if direction:
        currentPos += smallStep
    else:
        currentPos -= smallStep

    # if abs(currentPos + stepToPos) > FULL_TURN:
    #     stepToPos -= currentPos + stepToPos - FULL_TURN
    # while stepsToTake > 0:
    #     stepOnce()
    #     stepsToTake -= 1
    # set new position


def reverseDir():
    global direction
    if direction == 1:
        direction = 0
    else:  # value == 0
        direction = 1

        # async def stepOnce(time):
        #     await asyncio.sleep(time * 0.1)
        #     return True

        # send first steps
        # check next value
        # if value is close adjust end values
        # if value is far in same direction then add to end values
        # if value is far in opposite direction, then drop rest of steps and change dir, and remake array


# currentPos = 2


# makeQueue(-10)
# print(stepArr)
checkList(0)
checkList(50)
checkList(0)
checkList(0)
checkList(-51)
checkList(0)
# checkList(52)
# checkList(40)
# checkList(40)
# checkList(40)
# checkList(40)
# checkList(40)
# checkList(0)
# checkList(0)
# print(currentStep)
# checkList(0)
# checkList(0)
# print(currentStep)
# checkList(0)
# checkList(40)
# checkList(0)
# checkList(-90)
# checkList(1)
