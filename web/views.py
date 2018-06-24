import os
import time
import json
from flask import Response, request
from web.app import app
from web import storage
import settings


@app.route("/")
def hello():
    return "Hello World!"


@app.route("/questions")
def list_questions():
    questions = storage.download_current_questions()
    return Response(json.dumps(questions))

@app.route("/answers/<question_number>")
def get_answers(question_number):
    print("views, get_answers", question_number)
    answers = storage.get_answers(question_number)
    return Response(json.dumps(answers))



@app.route("/answer/<question_number>")
def get_answer(question_number):
    print("views, get_answer", question_number)
    answers = storage.get_random_answer(question_number)
    return Response(json.dumps(answers))


@app.route("/upload/<type_of_file>/<filename>", methods=["POST"])
def upload(type_of_file, filename):
    """
    uploads to either answers or questions to s3
    """
    filedir = os.path.join(settings.RECORDINGS_DIR, "%ss" % type_of_file)
    filepath = os.path.join(filedir, filename)

    storage.upload(filepath, folder=type_of_file)
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
        if not os.path.isdir('/tmp'):
            os.mkdir('/tmp')
        new_question = json.loads(request.data.decode())['data']
        with open(local_filepath, "w+") as f:
            f.write(new_question)
        question = storage.get_current_question_by_number(question_number)
        if question:
            # if question exists at this number
            folder, old_question_name = question.split('/')
            # move question to archive
            storage.move_file(question, "%s/%s" % ("questions", old_question_name))

        storage.upload(local_filepath, folder="current")

        # delete file locally
        os.remove(local_filepath)
        return Response("ok")
    except Exception as e:
        return Response(e)

