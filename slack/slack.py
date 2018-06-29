import requests
import json
from slackclient import SlackClient
from settings import SLACK_API_TOKEN, SLACK_CHANNEL_ID, SLACK_BOT_ID, SLACK_BOT_NAME

available_commands = """
*Available Commands*
--------------------
`list questions` - get a list of questions \n
`list answers <number>` - get a list of answers to current question number \n
`change question <number> <question>` - replace question at number \n
`help` - get this message
"""

sc = SlackClient(SLACK_API_TOKEN)

def post(message, channel=SLACK_CHANNEL_ID):
    sc.api_call(
      "chat.postMessage",
      channel=channel,
      text=message)


def check_messages():
    messages = sc.rtm_read()
    for m in messages:
        print(m.get('text', ''))
        if "<@%s>" % SLACK_BOT_ID not in m.get('text', ''):
            return

        kwargs = {
            'channel': m.get('channel', SLACK_CHANNEL_ID),
            'username': SLACK_BOT_NAME,
            'unfurl_links': True,
            'icon_emoji': ":phone:"}

        command = m.get('text', '').split("<@%s> " % SLACK_BOT_ID)[1]
        if "list" in command:
            if command == "list questions":
                res = requests.get("http://localhost:5000/questions")
                questions = json.loads(res.text)
                q_str = ""
                for q in questions:
                    q_str += "*%s* - %s\n" % (q, questions[q])
                sc.api_call("chat.postMessage", text=q_str, **kwargs)
            elif "list answers" in command:
                command_parts = command.split(' ')
                number = command_parts[2]
                response = requests.get("http://localhost:5000/answers/%s" % number)
                sc.api_call("chat.postMessage", text=response.text, **kwargs)
        elif "change question" in command:
            command_parts = command.split(' ')
            number = command_parts[2]
            new_question = " ".join(command_parts[3:])
            response = requests.post("http://localhost:5000/change_current/%s" % number, json={'data': new_question})
            sc.api_call("chat.postMessage", text=response.text, **kwargs)

        elif "get answer" in command:
            command_parts = command.split(' ')
            number = command_parts[2]

            response = requests.get("http://localhost:5000/answer/%s" % number)
            local_filepath = json.loads(response.text)
            sc.api_call("files.upload",
                        file=open(local_filepath, 'rb'),
                        display_as_bot=True,
                        channels=[SLACK_CHANNEL_ID],
                        **kwargs)
        elif command == "help":
            sc.api_call("chat.postMessage", text=available_commands, **kwargs)


