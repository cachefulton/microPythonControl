from machine import Pin
from rp2 import PIO, StateMachine, asm_pio  # Is used to make PIO programs


class LinearActuator:
    def __init__(self, pin1, pin2, enPin1, enPin2, smNum=2, smFreq=5000):
        """
        pin1 and pin2 MUST be sequential gpio pins, with pin1 being lower number (eg. pin1 = 18, pin2 = 19)
        """
        lyst = []
        for p in (pin1, pin2, enPin1, enPin2):
            if not isinstance(p, Pin):
                p = Pin(p, value=0, mode=Pin.OUT)
            lyst.append(p)
        self.pin1 = lyst[0]
        self.pin2 = lyst[1]

        self.enPin1 = lyst[2]
        self.enPin2 = lyst[3]
        # default breaks on
        self.lastPos = 100  # 0 - 100 to keep track of position of actuator
        # MAX_DELAY = the amount of loops the sm0 takes to till at full extension or full close
        # for simplicity I am setting the max delay to match the max position
        self.MAX_DELAY = 100

        self.sm0 = StateMachine(
            smNum,  # Creates object called sm_0 and binds it to state machine number in PIO block 0
            self.delay,  # Assigns step_counter as PIO program/function
            freq=smFreq,  # Sets the PIO frequency to sm_freq
            set_base=self.pin1,  # used for the first pin of the set() instruction
        )

        self.activateSM()
        self.pullHighEnable()
        # make sure the linear actuator is at position 100

    @asm_pio(
        set_init=(PIO.OUT_LOW, PIO.OUT_LOW),  # will use both gpio pins
        fifo_join=PIO.JOIN_TX,
    )  # Assembly decorator, pins default Low
    # function for sm0
    # fifo_join=PIO.JOIN_TX joins the RX fifo to the TX which means the sm TX queue can be 8 words long
    # this function is calibrated specifically for the distance of our linear actuator at frequency 5000
    # if 100 is passed into TX fifo then it will go the max distance it should
    # TODO calibrate this delay with more or less nop(), so that 100 passed into it is full brake
    def delay():
        pull(block)
        mov(y, osr)  # copy OSR data into y (load our direction into y)
        pull(block)
        mov(x, osr)  # copy OSR data into x (load our delay into x)
        jmp(not_y, "extend")
        set(pins, 0b10)
        jmp(y_dec, "retract")
        label("extend")
        set(pins, 0b01)
        label("retract")
        label("delay")
        nop()[20]
        nop()[19]
        jmp(x_dec, "delay")
        set(pins, 0b00)  # set both pin1 and pin2 low to stop actuator

    def setBrake(self, position):
        """
        takes an integer between 0 - 100,
        0 = no brakes, 100 = full brakes,
        position and delay to position are equal
        NOTE: only works if MAX_DELAY is == 100
        """

        delay = abs(self.lastPos - position)
        # delay = round(tempPos * self.MAX_DELAY / 100)
        if self.lastPos > position:
            self.retract(delay)
            self.lastPos = position
        elif self.lastPos < position:
            self.extend(delay)
            self.lastPos = position
        # else if self.lastPos == position then do nothing

    def retract(self, delay):
        # To retract pass not 0 to state machine
        self.sm0.put(1)
        self.sm0.put(delay)

    def extend(self, delay):
        # To extend pass 0 to state machine
        self.sm0.put(0)
        self.sm0.put(delay)

    def pullHighEnable(self):
        self.enPin1.value(1)
        self.enPin2.value(1)

    def pullLowEnable(self):
        self.enPin1.value(0)
        self.enPin2.value(0)

    def activateSM(self):
        self.sm0.active(1)

    def deactivateSM(self):
        self.sm0.restart()
        self.sm0.active(0)

    def reset(self):
        """
        Call this to reset linear actuator after unexpected power off
        Takes linear actuator to zero and then back to full
        """
        self.retract(self.MAX_DELAY)
        self.extend(self.MAX_DELAY)
