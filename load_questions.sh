cd /home/pi/lil-record
export GOOGLE_APPLICATION_CREDENTIALS=/home/pi/lil-record/settings/keys/lil-record.json
export PYTHONPATH=$PYTHONPATH:$PWD ; python3 record/load_questions.py
