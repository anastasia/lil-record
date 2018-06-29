from slack import slack
if __name__ == "__main__":
    import time
    if slack.sc.rtm_connect():
        print('connected')
        while True:
            slack.check_messages()
            time.sleep(1)
