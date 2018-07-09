import os
try:
    while True:
        exitcode = os.system('aplay --device=plughw:0 %s' % '/home/pi/lil-record/recordings/instructions/dialtone.wav')
        print("exitcode", exitcode)
        if exitcode:
            break
except KeyboardInterrupt:
    print('Goodbye')