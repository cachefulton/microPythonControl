import select
import sys
import time

# pip install thonny

# Set up the poll object
poll_obj = select.poll()
poll_obj.register(sys.stdin, select.POLLIN)

# Loop indefinitely
while True:
    # Wait for input on stdin
    poll_results = poll_obj.poll(
        1
    )  # the '1' is how long it will wait for message before looping again (in microseconds)
    if poll_results:
        # Read the data from stdin (read data coming from PC)
        data = sys.stdin.readline()
        # Write the data to the input file
        sys.stdout.write("received data: " + data + "\r")
    else:
        # do something if no message received (like feed a watchdog timer)
        continue

# from machine import Pin, PWM
# from utime import sleep

# pin = Pin("LED", Pin.OUT)

# print("LED starts flashing...")
# while True:
#     try:
#         pin.toggle()
#         sleep(1) # sleep 1sec
#     except KeyboardInterrupt:
#         break
# pin.off()
# print("Finished.")

# create PWM object from a pin and set the frequency of slice 0
# and duty cycle for channel A
pwm0 = PWM(Pin(0), freq=2000, duty_u16=32768)
pwm0.freq()  # get the current frequency of slice 0
pwm0.freq(1000)  # set/change the frequency of slice 0
pwm0.duty_u16()  # get the current duty cycle of channel A, range 0-65535
pwm0.duty_u16(200)  # set the duty cycle of channel A, range 0-65535
pwm0.duty_u16(0)  # stop the output at channel A
print(pwm0)  # show the properties of the PWM object.
pwm0.deinit()  # turn off PWM of slice 0, stopping channels A and B
# to get this to run automatically on boot up save as main.py on pico in thonny


# check to recieve signal
# send instructions to certain motor based on signal via pwm
