from flask import Flask, Response

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello World!"

@app.route("/questions")
def questions_list():
    a_list = ["question_1", "question_2", "question_3"]
    return Response(a_list)


