import base64
import io
import json
import os
import tempfile
import wave

import speech_recognition as sr
from channels.generic.websocket import (AsyncWebsocketConsumer,
                                        WebsocketConsumer)
from pydub import AudioSegment
from speech_recognition.exceptions import UnknownValueError
from transcription.views import transcribe_from_file


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, bytes_data=None, text_data=None):
        msg = json.loads(text_data)
        text = msg.get('text')
        text = 'en-US' if text == 'en' else text
        audio_data = msg.get('audioBlob')
        audio_data = audio_data.split(',')[1]
        audio_data = base64.b64decode(audio_data)

        audio_data = io.BytesIO(audio_data)
        audio_segment = AudioSegment.from_file(audio_data)
        pcm_data = audio_segment.set_frame_rate(44100)
        pcm_data = pcm_data.set_sample_width(2)

        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav_file:
            temp_wav_file_path = temp_wav_file.name

            with wave.open(temp_wav_file_path, 'wb') as wave_file:
                wave_file.setnchannels(1)
                wave_file.setframerate(44100)
                wave_file.setsampwidth(2)
                wave_file.writeframes(pcm_data._data)

        # f = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        # f.write(bytes_data)
        # res = transcribe_from_file(f.name, 'tiny')
        # os.unlink(f.name)
        try:
            res = ''
            r = sr.Recognizer()
            with sr.AudioFile(temp_wav_file_path) as source:
                audio = r.record(source)
                res = r.recognize_google(audio, language=text)
        except UnknownValueError:
            print("Message is empty")
        finally:
            os.unlink(temp_wav_file_path)
        self.send(text_data=json.dumps({"message": res}))
