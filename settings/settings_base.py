S3_BUCKET = "lil-record"
S3_KEY = "secret_key"
S3_SECRET = "secret_secret"
S3_LOCATION = 'http://{}.s3.amazonaws.com/'.format(S3_BUCKET)

SLACK_API_TOKEN = "slack-token"
SLACK_CHANNEL_ID = "test-channel"
SLACK_BOT_NAME = "lil-record"
SLACK_BOT_ID = "bot-id"

# raspberry pi settings
RECORDINGS_DIR = "recordings"
ANSWERS_DIR = "%s/%s" % (RECORDINGS_DIR, "answers")
QUESTIONS_DIR = "%s/%s" % (RECORDINGS_DIR, "questions")
INSTRUCTIONS_DIR = "%s/%s" % (RECORDINGS_DIR, "instructions")

SOUND_CARD = 0
