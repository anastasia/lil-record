import os
import time
import json
import subprocess
import requests
import RPi.GPIO as GPIO


RECORDINGS_DIR = "recordings"
ANSWERS_DIR = "%s/%s" % (RECORDINGS_DIR, "answers")
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

recordings_dir = "/home/pi/recordings"
questions_dir = os.path.join(recordings_dir, "questions")
# answers_dir = os.path.join(recordings_dir, "answers")

questions = []
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
    code = os.system('aplay --device=plughw:0,0 %s' % filename)
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
    global c, operator_has_been_called, action
    if GPIO.input(BOSS_PIN) == GPIO.HIGH and c != 0:
        print("resetting!")
        c = 0
    else:
        if c == 0:
            return

        if c < 10 and GPIO.input(RECV_PIN) == GPIO.LOW and action:
            operator_has_been_called = True
            play_question(c)

        elif c == 10 and GPIO.input(RECV_PIN) == GPIO.LOW and action:
            if not operator_has_been_called:
                call_operator()
            else:
                record_answer(c)


def create_answers_filename(question):
    """
    Writing filename locally
    """
    name, filetype = question.split('.')
    millis = int(round(time.time() * 1000))
    filename = "%s_%s.wav" % (name, str(millis))
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


def record_answer(count):
    global current_question
    filename = create_answers_filename(current_question)
    filename_path = os.path.join(ANSWERS_DIR, filename)
    record(filename_path)
    url = "http://localhost:5000/upload/%s/%s" % ("answers", filename)
    response = requests.post(url)
    print("response:", response)
    os.remove(filename_path)


def play_question(count):
    global action, questions_dir, current_question
    action = False
    questions = get_all_questions()
    for filename in questions:
        if filename[0:2] == "%s_" % str(count):
            question_to_ask = questions[filename]
            current_question = filename
            text_to_speech(question_to_ask)
            time.sleep(3)
            break


def call_operator():
    global action, questions_directory, operator_has_been_called
    action = False
    operator_has_been_called = True
    play(os.path.join(recordings_dir, "instructions.wav"))
    
    
def count(pin):
    global c, action
    action = True
    c = c + 1
    print("counting", c)


def get_all_questions():
    url = "http://localhost:5000/questions"
    result = requests.get(url)
    questions = json.loads(result.text)
    return questions


pid = subprocess.Popen(['python3', './killer.py'],
                 stdout=open('/dev/null', 'w'),
                 stderr=open('killer.log', 'a'),
                 preexec_fn=os.setpgrp
                 ).pid
print("killer pid", pid)

print("killer on the loose!!!")
GPIO.add_event_detect(BOSS_PIN, GPIO.BOTH, callback=main)
GPIO.add_event_detect(COUNT_PIN, GPIO.FALLING, callback=count, bouncetime=85)

try:
    while True:
        time.sleep(50000)
except KeyboardInterrupt:
    print('Goodbye')
    os.system("kill -9 %s" % pid)


GPIO.remove_event_detect(BOSS_PIN)
GPIO.remove_event_detect(COUNT_PIN)
GPIO.remove_event_detect(RECV_PIN)
