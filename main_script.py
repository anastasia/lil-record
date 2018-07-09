import os
import time
import json
import subprocess
import requests
import RPi.GPIO as GPIO
from settings import ANSWERS_DIR, QUESTIONS_DIR, INSTRUCTIONS_DIR

SOUND_CARD = 0
COUNT_PIN = 24
BOSS_PIN = 17
RECV_PIN = 13

GPIO.setwarnings(True)
GPIO.setmode(GPIO.BCM)

# rotary pins
GPIO.setup(COUNT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BOSS_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
# receiver up down
GPIO.setup(RECV_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

c = 0

answers = []
current_question = ''

operator_has_been_called = False

# prevents action from happening twice,
# like recording or playing back twice
action = True


def text_to_speech(text):
    """
    Plays text using sound card
    """
    cmd = 'espeak -s110 "%s" --stdout | aplay -D sysdefault:CARD=%s' % (text, SOUND_CARD)
    os.system(cmd)


def play(filename):
    print("getting filename", filename)
    code = os.system('aplay --device=plughw:0 %s' % filename)
    return code


def record(filename):
    code = os.system('arecord --device=plughw:0,0 --format=S16_LE --rate 44100 -V mono %s' % filename)
    return code


def main(pin):
    """
    10 - Call operator if not called
    10 - Record answer to questions
       - all other numbers: play question
    """
    global c, action
    if GPIO.input(BOSS_PIN) == GPIO.HIGH and c != 0:
        print("resetting!")
        play_dialtone(13)
        c = 0
    else:
        if c == 0:
            play_dialtone(13)
            return
        
        if GPIO.input(RECV_PIN) == GPIO.LOW and action:
            time.sleep(1)
            if c < 10:
                play_question(c)

            elif c == 10:
                call_operator()


def create_answers_filename(question):
    """
    Writing filename locally
    """
    print("create_answers_filename", question)
    name, filetype = question.split('.')
    millis = int(round(time.time() * 1000))
    filename = "%s_%s.wav" % (name, str(millis))
    return filename


def record_question():
    print("preparing to record")
    # getting question filename
    questions = get_all_questions()
    highest_num = 0
    if len(questions) > 0:
        for q in questions:
            name = q.split('/')[-1]
            num = int(name.split('.wav')[0])
            if num > highest_num:
                highest_num = num
        highest_num += 1
    filename_fullpath = os.path.join(QUESTIONS_DIR, '%s.wav' % highest_num)
    print('getting ready to record question', filename_fullpath)
    record(filename_fullpath)
    print('done recording question')
    # handle end


def record_answer():
    global current_question
    filename = create_answers_filename(current_question)
    filename_path = os.path.join(ANSWERS_DIR, filename)
    record(filename_path)
    # url = "http://localhost:5000/upload/%s/%s" % ("answers", filename)
    # response = requests.post(url)
    # print("response:", response)
    # os.remove(filename_path)


def play_question(count):
    global action, current_question
    action = False
    questions = get_all_questions()
    print("calling method play_question", count)
    for filename in questions:
        # match dial count to question filename
        filename_count = filename.split("_")[0][-1]
        if filename_count == str(count):
            print("finding matching file")
            question_to_ask = filename
            current_question = filename.split("/")[-1]
            play(question_to_ask)
            # play "record your answer after the tone"
            play(os.path.join(INSTRUCTIONS_DIR, "record_instructions.wav"))
            play(os.path.join(INSTRUCTIONS_DIR, "beep.wav"))
            record_answer()


def call_operator():
    global action, operator_has_been_called
    action = False
    operator_has_been_called = True
    play(os.path.join(INSTRUCTIONS_DIR, "operator.wav"))
    play(os.path.join(INSTRUCTIONS_DIR, "beep.wav"))
    millis = int(round(time.time() * 1000))
    filename = "%s_%s.wav" % ("name", str(millis))
    name_filepath = os.path.join(ANSWERS_DIR, filename)
    print("recording name file %s", name_filepath)
    record(name_filepath)
    
    
def count(pin):
    global c, action
    action = True
    kill_dialtone()
    c = c + 1
    print("counting", c)


def get_all_questions():
    print(os.listdir(QUESTIONS_DIR))
    questions = [os.path.join(QUESTIONS_DIR, f) for f in os.listdir(QUESTIONS_DIR) if f.endswith(".wav")]
    return questions


def play_dialtone(pin):
    if GPIO.input(RECV_PIN) == GPIO.LOW:
        pid = subprocess.Popen(['python3', '/home/pi/lil-record/dialtone.py'],
              stdout=open('/dev/null', 'w'),
              stderr=open('/dev/null', 'w'),
              preexec_fn=os.setpgrp
              ).pid
        print("dialtone", pid)

def kill_dialtone():
    res = subprocess.check_output('ps aux | grep dialtone.py | grep -v grep | tr -s " " | cut -d " " -f 2 ', shell=True)
    pids = res.decode().split('\n')[0:-1]
    print("killing pids:", pids)
    [os.system('kill %s' % pid) for pid in pids]
    os.system('killall aplay')

    
# play_dialtone()
GPIO.add_event_detect(13, GPIO.BOTH, callback=play_dialtone, bouncetime=10)
GPIO.add_event_detect(BOSS_PIN, GPIO.BOTH, callback=main)
GPIO.add_event_detect(COUNT_PIN, GPIO.FALLING, callback=count, bouncetime=75)

try:
    while True:
        time.sleep(50000)
except KeyboardInterrupt:
    print('Goodbye')


GPIO.remove_event_detect(BOSS_PIN)
GPIO.remove_event_detect(COUNT_PIN)
GPIO.remove_event_detect(RECV_PIN)
print("ran script")
