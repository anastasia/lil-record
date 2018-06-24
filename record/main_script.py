import os
import time
import random
import subprocess
import requests
import RPi.GPIO as GPIO
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
answers_dir = os.path.join(recordings_dir, "answers")

questions = []
answers = []
current_question = ''

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
    filename = "%s_%s.wav" % (question, time.asctime().replace(' ', '_'))
    global answers_directory
    filename_fullpath = os.path.join(answers_dir, filename)
    return filename_fullpath


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
    # pop question from list
    current_question = questions[random.randrange(0, len(questions))]
    current_number = current_question.split('.wav')[0]
    question_file = os.path.join(questions_dir, current_question)

    code = play(question_file)
    # if we got a return code that's not zero, that means
    # the user tried to exit out by hanging up. Exit.
    if code > 0:
        return
    # wait
    time.sleep(5)
    # play beep
    print(' ======> BEEEEEEEEP <====== ')
    # play(os.path.join(recordings_dir, 'beep.wav'))


    # record answer

    filename = create_answers_filename(current_number)
    record(filename)
    url = "http://localhost:5000/upload/%s/%s" % ("answers", filename)
    response = requests.post(url)
    print("response:", response)
    os.remove(filename)


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
    global questions_dir
    contents = os.listdir(questions_dir)
    recordings = []
    for q in contents:
        filename, file_extension = os.path.splitext(q)
        if file_extension == '.wav':
            recordings.append("%s/%s" % (questions_dir, q))
    return contents


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
