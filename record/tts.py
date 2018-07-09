import os
import random
from settings import QUESTIONS_DIR

# export=GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials
def synthesize_text(text, output_filename, output_dir=QUESTIONS_DIR, voice=None):
    """
    Synthesizes speech from the input string of text.
    Female voice = 0, Male voice = 1
    output filename doesn't need extension
    """
    from google.cloud import texttospeech_v1beta1 as texttospeech
    client = texttospeech.TextToSpeechClient()

    input_text = texttospeech.types.SynthesisInput(text=text)

    genders = (texttospeech.enums.SsmlVoiceGender.FEMALE, texttospeech.enums.SsmlVoiceGender.MALE)
    if not voice:
        gender = genders[random.randrange(0, 2)]
    else:
        gender = genders[voice]

    # Note: the voice can also be specified by name.
    # Names of voices can be retrieved with client.list_voices().
    voice = texttospeech.types.VoiceSelectionParams(
        language_code='en-US',
        ssml_gender=gender)

    audio_config = texttospeech.types.AudioConfig(
        audio_encoding=texttospeech.enums.AudioEncoding.MP3)

    response = client.synthesize_speech(input_text, voice, audio_config)

    # The response's audio_content is binary.
    mp3_filepath = os.path.join(output_dir, "%s.mp3" % output_filename)
    with open(mp3_filepath, 'wb') as out:
        out.write(response.audio_content)
        print('Audio content written to file %s' % mp3_filepath)
    
    wav_name = os.path.join(output_dir, "%s.wav" % output_filename)
    print('Audio content re-written to file %s' % wav_name)
    os.system("mpg321 -w %s %s" % (wav_name, mp3_filepath))
    print('Deleting mp3')
    os.remove(mp3_filepath)

