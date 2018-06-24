import os
import time
import random
import subprocess
import requests
import RPi.GPIO as GPIO
from settings import *
GPIO.setwarnings(True)
GPIO.setmode(GPIO.BCM)

# rotary pins
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
# receiver up down
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

c = 0

recordings_dir = "/home/pi/recordings"
questions_dir = os.path.join(recordings_dir, "questions")
# answers_dir = os.path.join(recordings_dir, "answers")

questions = []
answers = []
current_question = ''

def text_to_speech(text):
    """
    Plays text using sound card
    """
    cmd = 'espeak -s110 “%s” —stdout | aplay -D systemdefault:CARD=%s' % (text, SOUND_CARD)
    os.system(cmd)

def play(filename):
    print("getting filename", filename)
    code = os.system('aplay --device=plughw:0,0 %s' % filename)
    return code

def record(filename):
    code = os.system('arecord --device=plughw:0,0 --format=S16_LE --rate 44100 -V mono %s' % filename)
    return code

# GPIO.input(13) == GPIO.LOW => receiver is off the hook
# GPIO.input(13) == GPIO.LOW => receiver is on the hook

# prevents action from happening twice,
# like recording or playing back twice 
action = True

def main(pin):
    global c
    if GPIO.input(18) == GPIO.HIGH and c != 0:
        print("resetting!")
        c = 0
    else:
        # 1 record answer
        # 2 record question
        # 3 listen to question
        if c == 0:
            return
        if c < 10 and c != 8 and GPIO.input(13) == GPIO.LOW and action:
            play_question(c)
            
        elif c == 8 and GPIO.input(13) == GPIO.LOW and action:
            record_question()
            
        elif c == 10 and GPIO.input(13) == GPIO.LOW and action:
            call_operator()
            
        # print('counted', c)


def create_answers_filename(question):
    """
    Writing filename locally
    """
    # get local question
    filename = "%s_%s.wav" % (question, time.asctime().replace(' ', '_'))
    return filename


def record_question():
    print("preparing to record")
    # getting question filename
    global questions_dir
    questions = get_all_questions()
    highest_num = 0
    if len(questions) > 0:
        for q in questions:
            name = q.split('/')[-1]
            num = int(name.split('.wav')[0])
            if num > highest_num:
                highest_num = num
        highest_num += 1
    filename_fullpath = os.path.join(questions_dir, '%s.wav' % highest_num)
    print('getting ready to record question', filename_fullpath)
    record(filename_fullpath)
    print('done recording question')
    # handle end

def play_question(count):
    global action, questions_dir
    action = False
    questions = get_all_questions()

    question_to_ask = questions[count]

    text_to_speech(question_to_ask)
    # wait
    time.sleep(3)
    # play beep
    print(' ======> BEEEEEEEEP <====== ')
    # play(os.path.join(recordings_dir, 'beep.wav'))


    # record answer

    filename = create_answers_filename(current_number)

    filename_path = os.path.join(ANSWERS_DIR, filename)
    record(filename_path)
    url = "http://localhost:5000/upload/%s/%s" % ("answers", filename)
    response = requests.post(url)
    print("response:", response)
    os.remove(filename_path)


def call_operator():
    global action, questions_directory
    action = False
    play(os.path.join(recordings_dir, "instructions.wav"))
    
    
def count(pin):
    global c, action
    action = True
    c = c + 1
    print("counting", c)


def get_all_questions():
    url = "http://localhost:5000/questions"
    questions = requests.get(url)
    # global questions_dir
    # contents = os.listdir(questions_dir)
    # recordings = []
    # for q in contents:
    #     filename, file_extension = os.path.splitext(q)
    #     if file_extension == '.wav':
    #         recordings.append("%s/%s" % (questions_dir, q))
    # return contents
    return questions

def end_script(pin):
   print("end script!")
   # get_all_questions()


pid = subprocess.Popen(['python3', './killer.py'],
                 stdout=open('/dev/null', 'w'),
                 stderr=open('killer.log', 'a'),
                 preexec_fn=os.setpgrp
                 ).pid
print("killer pid", pid)

print("killer on the loose!!!")
GPIO.add_event_detect(13, GPIO.RISING, callback=end_script, bouncetime=10)
GPIO.add_event_detect(18, GPIO.BOTH, callback=main)
GPIO.add_event_detect(24, GPIO.FALLING, callback=count, bouncetime=85)

try:
    while True:
        time.sleep(50000)
except KeyboardInterrupt:
    print('Goodbye')
    os.system("kill -9 %s" % pid)


GPIO.remove_event_detect(18)
GPIO.remove_event_detect(24)
GPIO.remove_event_detect(13)
