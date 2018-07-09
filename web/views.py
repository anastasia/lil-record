import os
import time
import json
from flask import Response, request
from web.app import app
from web.storage import *
import settings


@app.route("/")
def hello():
    return "Hello World!"


@app.route("/questions")
def list_questions():
    questions = download_current_questions()
    return Response(json.dumps(questions))


@app.route("/questions/<question_number>")
def get_question_at_number(question_number):
    question = get_current_question_by_number(question_number)
    return Response(question)

# get all answers' names
@app.route("/answers/<question_number>")
def get_all_answers(question_number):
    print("views, get_answers", question_number)
    answers = get_answers(question_number)
    return Response(json.dumps(answers))

# get single answer
@app.route("/answer/<question_number>")
def get_answer(question_number):
    print("views, get_answer", question_number)
    answers = get_random_answer(question_number)
    return Response(json.dumps(answers))


@app.route("/upload/<type_of_file>/<filename>", methods=["POST"])
def upload_file(type_of_file, filename):
    """
    uploads to either answers or questions to s3
    """
    filedir = os.path.join(settings.RECORDINGS_DIR, "%ss" % type_of_file)
    filepath = os.path.join(filedir, filename)

    upload(filepath, folder=type_of_file)
    return Response("ok")


@app.route("/change_current/<question_number>", methods=["POST"])
def change_current(question_number):
    """
    post new question to question number
    curl --data "data=New question?" http://lilrecord.website/change_current/2
    """
    try:
        millis = int(round(time.time() * 1000))
        filename = "%s_%s.txt" % (question_number, millis)
        local_filepath = "/tmp/%s" % filename
        print("local_filepath %s" % local_filepath)
        if not os.path.isdir('/tmp'):
            os.mkdir('/tmp')
        new_question = json.loads(request.data.decode())['data']
        print("new_question %s" % new_question)
        with open(local_filepath, "w+") as f:
            f.write(new_question)
        with open(local_filepath, "r") as f:
            print(f.read())
            
        
        question = get_current_question_filename(question_number)
        if question:
            # if question exists at this number
            folder, old_question_name = question.split('/')
            # move question to archive
            move_file(question, "%s/%s" % ("questions", old_question_name))
            
            
        upload(local_filepath, folder="current")
        os.system("bash /home/pi/lil-record/load_questions.sh")
        # delete file locally
        os.remove(local_filepath)
        return Response("ok")
    except Exception as e:
        return Response(e)

