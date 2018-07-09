import os
from settings import ANSWERS_DIR
from web.storage import upload

def main():
    """
    upload answers to s3
    delete them from local
    """
    answers = [ os.path.join(ANSWERS_DIR, f) for f in os.listdir(ANSWERS_DIR)]
    for answer in answers:
        print('uploading %s' % answer)
        upload(answer, folder='answers')
        print('deleting %s', answer)
        os.remove(answer)
        
        
if __name__ == "__main__":
    main()
