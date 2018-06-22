import os
import time
import RPi.GPIO as GPIO

GPIO.setwarnings(True)
GPIO.setmode(GPIO.BCM)

GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def end_script(pin):
   print("stopping script")
   os.system('killall arecord')
   os.system('killall aplay')

GPIO.add_event_detect(13, GPIO.RISING, callback=end_script, bouncetime=10)

try:
    while True:
        time.sleep(50000)
except KeyboardInterrupt:
    print('Goodbye')

GPIO.remove_event_detect(13)
