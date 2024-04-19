import os
# import sounddevice
import pyaudio
import torchaudio
import azure.cognitiveservices.speech as speechsdk

speech_key, service_region = os.environ['SPEECH_KEY'], os.environ['SPEECH_REGION']
from_language, to_languages = 'en-US', [ 'de', 'fr']
language_to_voice_map = {
    "de": "de-DE-KatjaNeural",
    "fr": "en-US-AvaMultilingualNeural",
}
 
use_default_speaker=True
use_default_microphone=True

def system_config():
    print("Nothing explicitly configured")


def translate_speech_to_text():
    translation_config = speechsdk.translation.SpeechTranslationConfig(
            subscription=speech_key, region=service_region)

    translation_config.speech_recognition_language = from_language
    for lang in to_languages:
        translation_config.add_target_language(lang)

    translation_recognizer = speechsdk.translation.TranslationRecognizer(
            translation_config=translation_config)
    
    print('Say something...')
    result = translation_recognizer.recognize_once()
    return result


def synthesize_translations(result):
    print(f'Recognized: "{result.text}"')

    for language in result.translations:
        translation = result.translations[language]
        print(f'Translated into "{language}": {translation}')

        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
        speech_config.speech_synthesis_voice_name = language_to_voice_map.get(language)
        
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
        speech_synthesizer.speak_text_async(translation).get()

def synthesize_one_language(translation, language, audio_config):
    print(f'Translated into "{language}": {translation}')
    
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    speech_config.speech_synthesis_voice_name = language_to_voice_map.get(language)
        
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    return speech_synthesizer.speak_text_async(translation).get()          


translationspeech = {}
# Set up PyAudio
print("Setting up audio")
p = pyaudio.PyAudio()

translated_speech = translate_speech_to_text()
for language in translated_speech.translations: 
    # Set up the audio stream
    pull_stream = speechsdk.audio.PullAudioOutputStream()
    output_destination = speechsdk.audio.AudioOutputConfig(stream = pull_stream)

    translationspeech[language] = synthesize_one_language(translation = translated_speech.translations[language], language = language, audio_config = output_destination)

print("Now the data is synthesized")

print("Now we combine left and right")
wfm_length=len(translationspeech[to_languages[0]].audio_data)
wfm_length = min(wfm_length, len(translationspeech[to_languages[1]].audio_data))
#wfm_length = 65535
#for language in translated_speech.translations:
#    wfm_length = min(wfm_length, len(translationspeech[language].audio_data))
print(wfm_length)
left_stream = translationspeech[to_languages[0]].audio_data[44:]
right_stream = translationspeech[to_languages[1]].audio_data[44:]
stereo_stream = [0] * 4*wfm_length
wfm_length -= 44 # because of header
offset = 0
while offset < wfm_length-8:
    stereo_stream[offset*2] = left_stream[offset]
    stereo_stream[offset*2+1] = left_stream[offset+1]
    stereo_stream[offset*2+2] = right_stream[offset]
    stereo_stream[offset*2+3] = right_stream[offset+1]
    offset += 2
    if ((offset % 1000) == 0):
        print(offset)

print("Opening stream")
stream = p.open(format=p.get_format_from_width(2), channels=1, rate=16000, output=True)

chunk_size = 256
offset = 0
while offset < len(left_stream):
    chunk = left_stream[offset:offset + chunk_size]
    stream.write(chunk)
    offset += chunk_size

chunk_size = 256
offset = 0
while offset < len(left_stream):
    chunk = right_stream[offset:offset + chunk_size]
    stream.write(chunk)
    offset += chunk_size

stream.stop_stream()
stream.close()

stream = p.open(format=p.get_format_from_width(2), channels=2, rate=16000, output=True)

chunk_size = 256
offset = 0
while offset < len(stereo_stream):
    chunk = stereo_stream[offset:offset + chunk_size]
    stream.write(bytes(chunk))
    offset += chunk_size

stream.stop_stream()
stream.close()

#for language in translated_speech.translations:
#    audio_data = translationspeech[language].audio_data
# 
#    metadata = torchaudio.info(audio_data)
#    print(metadata)
#    print("Sending data to audio")
###    chunk_size = 256  # Adjust the chunk size as needed
#    offset = 0
#    while offset < len(audio_data):
#        chunk = audio_data[offset:offset + chunk_size]
#        stream.write(chunk)
#        offset += chunk_size


# Clean up
p.terminate()



