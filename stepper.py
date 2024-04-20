# keep track of position
# but don't rely on turning all the way to position
# splits step to into 10 and turns a tenth of the way, and then should check to see if any changes
# update go to position dynamically so no lag happens

# our controller is max 500kHz
# motor is 1.8 degrees per step, we set the pins to
# this class counts on the pulses/rev to be on 200 setting (see manual fot CL57T stepper controller)

from machine import Pin
from rp2 import PIO, StateMachine, asm_pio  # Is used to make PIO programs


# TODO see if we are using the enable pin and implement it
class Stepper:
    def __init__(self, stepPin, dirPin, enablePin, smNum0=0, smNum1=1, freq=225000):
        lyst = []
        for p in (stepPin, dirPin, enablePin):
            if not isinstance(p, Pin):
                p = Pin(p, value=0, mode=Pin.OUT)
            lyst.append(p)
        self.stepPin = lyst[0]
        self.dirPin = lyst[1]
        self.enablePin = lyst[2]  # TODO currently not using enable pin
        self.checkSMDone = True  # to check if state machine 0 is done
        self.stepQueue = []  # will add steps here and clear it if direction changes
        self.lastStepToPos = 0
        self.currentPos = 0  # will be from -FULL_TURN to FULL_TURN
        self.direction = 0  # will be 0 for CW or 1 for CCW, default is 0
        # now we have a 50 to 1 gear box, so each full rotation is 10000 steps, with the stepper turning once at 200 steps
        self.FULL_TURN = 25500  # just over 2.5 revolutions, TODO change this to be the right number for tug wheels
        self.freq = freq  # stepSpeed (sm1) frequency

        # 1_000_000 Hz = 1 MHz means each instruction in PIO is 1us long
        # 4_000_000 Hz = 4 MHz means each instruction in PIO is 0.25 us long

        self.sm0 = StateMachine(
            smNum0,  # Creates object called sm_0 and binds it to state machine 0 in PIO block 0
            self.dirChangeStepCount,  # Assigns step_counter as PIO program/function
            freq=200000,  # Sets the PIO frequency
            sideset_base=self.stepPin,  # Sets stepPin as first sideset pin of PIO program/function
            set_base=self.dirPin,  # used for the first pin of the set() instruction
        )

        self.sm1 = StateMachine(
            smNum1,  # Creates object called sm_1 and binds it to state machine 1 in PIO block 0
            self.stepSpeed,  # Assigns step_speed as PIO program/function
            freq=self.freq,  # Sets the PIO frequency to ss_freq
        )

        self.sm0.irq(
            self.sm0Handler
        )  # Directs interrupts from sm0 to the interrupt handler sm0Handler()

        self.activateSM()

    @asm_pio(
        sideset_init=PIO.OUT_LOW,
        set_init=PIO.OUT_LOW,
        fifo_join=PIO.JOIN_TX,
    )  # Assembly decorator, pins default Low
    # function for sm0
    # fifo_join=PIO.JOIN_TX joins the RX fifo to the TX which means the sm TX queue can be 8 words long
    # because I'm passing in two things at a time, the fifo can be 4 full sequences deep
    def dirChangeStepCount():
        pull(block)  # wait for FIFO to fill (put), then pull data to OSR
        mov(y, osr)  # copy OSR data into Y (load our direction into y)
        set(pins, 0)  # set pins off
        jmp(
            not_y, "off"
        )  # checks if y is zero and if it is then pins remain off, if not then pins turns on
        set(pins, 1)
        label("off")
        pull(block)  # wait for FIFO to fill (put), then pull data to OSR
        mov(x, osr)  # copy OSR data into X (load our steps into x)
        label("count")  # this is a header we jump back to for counting steps
        jmp(not_x, "end").side(1)[1]  # if x is 0(zero), jmp to end - Side Step Pin On
        irq(5).side(0)  # sets IRQ 5 high, starting step_speed() - Side Step Pin Off
        irq(block, 4)  # waiting for IRQ flag 4 to clear
        jmp(
            x_dec, "count"
        )  # if x is NOT 0(zero), remove one (-1) from x and jump back to count, else continue
        label("end")  # This is a header we can jmp to if x is 0.
        irq(
            block, rel(0)
        )  # Signals IRQ handler that all steps have been made and waits for handler to clear the flag (block)

    @asm_pio(autopull=True)  # Tells the program that this is a PIO program/function.
    # function for sm1
    def stepSpeed():
        wait(1, irq, 5)  # waiting for IRQ flag 5 from step_counter and then clears it
        set(y, 5)  # set y to the value 31 (which is 0-31 = 32)
        label("delay")  # this is a header we jump back to for adding a delay
        nop()[9]  # do nothing for [n] instructions (which is 20 instructions)
        jmp(
            y_dec, "delay"
        )  # if y not 0(zero), remove one (-1) from y make jump to delay, Else, continue
        irq(clear, 4)  # clear IRQ flag 4, allowing step_counter() to continue

    def sm0Handler(self, sm):
        self.checkSMDone = True
        self.takeSteps()

    def makeQueue(self, stepTo):
        """
        Takes the step to position and figures out how many steps to take to position.
        Then breaks the steps into a queue of 10 (stepQueue) instead of one big step.
        Will default clear the queue before making it
        """
        currentStep = 0
        queueLen = 10
        # get how many positive steps to take
        if (self.currentPos > 0 and stepTo > 0) or (
            self.currentPos < 0 and stepTo < 0
        ):  # if signs are the same
            currentStep = abs(abs(stepTo) - abs(self.currentPos))
        else:  # signs are different or one number is 0
            currentStep = abs(stepTo) + abs(self.currentPos)
        leftOver = currentStep % queueLen
        splitNum = currentStep // queueLen

        self.stepQueue.append(leftOver + splitNum)
        # I need to know these leftOver + splitNum
        if splitNum > 0:
            queueLen -= 1  # already appended 1 to queue before the loop below
            while queueLen > 0:
                self.stepQueue.append(splitNum)
                queueLen -= 1

    def takeSteps(self):
        """
        Takes current queue and direction and send it to sm0 fifo
        """
        if not self.stepQueue:
            return
        steps = self.stepQueue.pop(0)  # steps is always positive
        # put 2 things on the sm queue IN THAT ORDER
        # the put will stall program if sm0 fifo is full
        self.sm0.put(self.direction)
        self.sm0.put(steps)
        self.checkSMDone = False
        if self.direction:
            self.currentPos -= steps
        else:
            self.currentPos += steps

    def controlTurn(self, value):
        """
        Takes a value between -100 and 100, 0 is going strait.
        Compares the next position to current position and figures out direction.
        Remakes queue if needed and takes next steps if stateMachine0 is done.
        """
        stepToPos = int(value * self.FULL_TURN / 100)

        # if stepToPos has changed at all, clear queue, make sure direction is correct, and remake queue
        if self.lastStepToPos == stepToPos:
            return

        self.stepQueue = []  # the flag that tells sm0Handler not to run takeSteps
        if self.currentPos == stepToPos:  # don't turn the wheels anymore
            return
        # check direction
        if stepToPos > self.currentPos and self.direction == 1:
            self.direction = 0
        elif stepToPos < self.currentPos and self.direction == 0:
            self.direction = 1
        self.makeQueue(stepToPos)  # the flag that tells sm0Handler to run takeSteps
        self.lastStepToPos = stepToPos

        if self.checkSMDone:  # if smDone is ever true we need to takeSteps here
            self.takeSteps()

    def activateSM(self):
        self.sm0.active(1)
        self.sm1.active(1)
        self.sm0.restart()
        self.sm1.restart()

    def deactivateSM(self):
        self.sm0.active(0)
        self.sm1.active(0)
