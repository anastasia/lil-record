import os
import time
from flask import Flask, Response, request

from web.storage import move_file, download_current_questions, upload as s3_upload
import settings

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/questions")
def questions_list():

    a_list = ["question_1", "question_2", "question_3"]
    return Response(a_list)


@app.route("/upload/<type_of_file>/<filename>")
def upload(type_of_file, filename):
    """
    uploads to either answers or questions to s3
    """
    filedir = os.path.join(settings.RECORDINGS_DIR, "%ss" % type_of_file)
    filepath = os.path.join(filedir, filename)

    s3_upload(filepath, filename, folder=type_of_file)
    return Response("ok")


@app.route("/change_current/<question_number>", methods=["POST"])
def change_current(question_number):
    """
    post new question to question number
    curl --data "data=New question?" http://lilrecord.website/change_current/2
    """
    millis = int(round(time.time() * 1000))
    filename = "%s_%s.txt" % (question_number, millis)
    local_filepath = "/tmp/%s" % filename
    if not os.path.isdir('/tmp'):
        os.mkdir('/tmp')
    with open(local_filepath, "w+") as f:
        f.write(request.form['data'])
    questions = download_current_questions()
    for question in questions:
        folder, path = question.split('/')
        number, rest_of_path = path.split('_')
        if number == question_number:
            # move question to archive
            move_file(question, "%s/%s" % ("questions", path))

    s3_upload(local_filepath, folder="current")

    # delete file locally
    os.remove(local_filepath)

    return Response("ok")

