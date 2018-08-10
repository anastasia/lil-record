Just a lil-record
```bash
  $ cp settings_example.py settings.py
  $ mkvirtualenv lil-record
  $ pip install -r requirements.txt
```

All web related assets are in `/web`
To run:
```
  $ python run.py
```
    
All lil-record related (raspberry pi) assets are in `/record`



```
  $ systemctl status lilrecord.service
```
Starts up four processes:
- `python3 /home/pi/lil-record/main_script.py`

An event detection script responsible for reading all of the pins and basically allowing the raspberry pi to power a rotary phone

- `python3 /home/pi/lil-record/run.py`

The flask app that allows downloading questions from aws, uploading answers to aws  

- `python3 /home/pi/lil-record/run_slack.py`

Listens to slack messages for mention of @lil-record, executes commands

- `python3 /home/pi/lil-record/killer.py`

A script that interrupts audio recording and playing on receiver hangup
  
