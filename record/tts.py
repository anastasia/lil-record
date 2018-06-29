import os
import random
from settings import QUESTIONS_DIR

# export=GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials
def synthesize_text(text, output_filename, output_dir=QUESTIONS_DIR):
    """
    Synthesizes speech from the input string of text.
    """
    from google.cloud import texttospeech_v1beta1 as texttospeech
    client = texttospeech.TextToSpeechClient()

    input_text = texttospeech.types.SynthesisInput(text=text)

    genders = (texttospeech.enums.SsmlVoiceGender.MALE, texttospeech.enums.SsmlVoiceGender.FEMALE)
    gender = genders[random.randrange(0, 2)]

    # Note: the voice can also be specified by name.
    # Names of voices can be retrieved with client.list_voices().
    voice = texttospeech.types.VoiceSelectionParams(
        language_code='en-US',
        ssml_gender=gender)

    audio_config = texttospeech.types.AudioConfig(
        audio_encoding=texttospeech.enums.AudioEncoding.MP3)

    response = client.synthesize_speech(input_text, voice, audio_config)

    # The response's audio_content is binary.
    output_filepath = os.path.join(output_dir, "%s.mp3" % output_filename)
    with open(output_filepath, 'wb') as out:
        out.write(response.audio_content)
        print('Audio content written to file %s' % output_filepath)
