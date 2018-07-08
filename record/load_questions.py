import os
from settings import QUESTIONS_DIR
from web.storage import download_current_questions
from record.tts import synthesize_text


def main():
    """
    run script every half day
        => get questions list
        => download text questions locally
        => remove all old mp3 questions
        => transform into mp3s
        => play from local
    """

    print("loading questions")
    old_filelist = [f for f in os.listdir(QUESTIONS_DIR)]
    for file in old_filelist:
        os.remove(os.path.join(QUESTIONS_DIR, file))
    text_questions = download_current_questions()
    for qname in text_questions:
        name = qname.split(".txt")[0]
        synthesize_text(text_questions[qname], name)
        wav_name = os.path.join(QUESTIONS_DIR, name + ".wav")
        mp3_name = os.path.join(QUESTIONS_DIR, name + ".mp3")
        # convert files to .wav
        os.system("mpg321 -w %s %s" % (wav_name, mp3_name))

    text_filelist = [f for f in os.listdir(QUESTIONS_DIR) if f.endswith('.txt') or f.endswith('.mp3')]
    for txt in text_filelist:
        os.remove(os.path.join(QUESTIONS_DIR, txt))

if __name__ == "__main__":
    main()

