from picozero import Servo  # importing Servo class to easily control the servo motor
from time import sleep

# creating a Servo object
servo = Servo(15)

# continuously swing the servo arm to min, mid, and max positions (for a duration of 1 sec each)
while True:
    # swinging the servo arm to its min position
    servo.min()
    sleep(1)

    # swinging the servo arm to its mid position
    servo.mid()
    sleep(1)

    # swinging the servo arm to its max position
    servo.max()
    sleep(1)

    for i in range(0, 100):
        servo.value = i / 100
        sleep(0.1)

    servo.off()
