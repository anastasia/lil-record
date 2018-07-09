import os
import subprocess
import time
import RPi.GPIO as GPIO

GPIO.setwarnings(True)
GPIO.setmode(GPIO.BCM)

GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
def end_script(pin):
    if GPIO.input(13) == GPIO.HIGH:
        os.system('killall arecord')
        res = subprocess.check_output('ps aux | grep dialtone.py | grep -v grep | tr -s " " | cut -d " " -f 2 ', shell=True)
        pids = res.decode().split('\n')[0:-1]
        [os.system('kill %s' % pid) for pid in pids]
        # os.system('ps aux | grep dialtone.py | grep -v grep | awk \'{print $2}\' | xargs kill')
        os.system('killall aplay')


GPIO.add_event_detect(13, GPIO.RISING, callback=end_script, bouncetime=10)

try:
    while True:
        time.sleep(50000)
except KeyboardInterrupt:
    print('Goodbye')

GPIO.remove_event_detect(13)
