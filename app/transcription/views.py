from django.http import HttpResponse
from django.shortcuts import render
from TTS.api import TTS
from .serializers import AudioSerializer
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
import tempfile
import os
import whisper
import json
import translators as tr


def index(request):
    return render(request, "transcription/index.html")


class commandView(APIView):
    def post(self, request):
        file = request.FILES["audio"]

        with tempfile.NamedTemporaryFile(suffix=os.path.splitext(file.name)[1], delete=False) as f:
            for chunk in file.chunks():
                f.write(chunk)
            f.seek(0)

        model = whisper.load_model("medium")
        audio = whisper.load_audio(f.name)
        audio = whisper.pad_or_trim(audio)

        mel = whisper.log_mel_spectrogram(audio).to(model.device)
        options = whisper.DecodingOptions(fp16=False)

        command = whisper.decode(model, mel, options).text

        return Response("Success", status.HTTP_200_OK)


def process_command(command):
    # Translate command to English
    command = tr.translate_text(
        command, to_language='en', translator='google').lower()

    # Look for keywords
    if 'translate' in command:
        pass
    elif 'read' in command:
        pass


class processAudio(ViewSet):
    serializer_class = AudioSerializer

    def create(self, request):
        print("Got a request")
        file = request.FILES["audio"]
        to_language = request.data['to_language']
        print(to_language)
        if not file:
            return Response("No file provided", status=status.HTTP_400_BAD_REQUEST)

        with tempfile.NamedTemporaryFile(suffix=os.path.splitext(file.name)[1], delete=False) as f:
            for chunk in file.chunks():
                f.write(chunk)
            f.seek(0)
        try:
            model = whisper.load_model("small")
            audio = whisper.load_audio(f.name)
            audio = whisper.pad_or_trim(audio)

            mel = whisper.log_mel_spectrogram(audio).to(model.device)
            options = whisper.DecodingOptions(fp16=False)

            original = whisper.decode(model, mel, options).text
            translated = tr.translate_text(
                original, to_language=to_language, translator='google')

        finally:
            os.unlink(f.name)

        data = {
            'original': original,
            'translated': translated
        }

        return Response(data, status=status.HTTP_200_OK)


class getAudioResponse(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, format=None):
        prompt = request.data['prompt']
        to_language = request.data['to_language']
        audio_data, path = generate_tts(prompt, to_language)

        response = HttpResponse(audio_data, content_type='audio/wav')
        response['Content-Disposition'] = f'attachment; filename={path}'

        return response


def generate_tts(text, to_language='pl'):
    # Translate to destination language
    text = tr.translate_text(
        text, to_language=to_language, translator='google')

    # Create a file with read translation
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
        if to_language == 'pl':
            tts = TTS(model_name="tts_models/pl/mai_female/vits")
            tts.tts_to_file(text=text, file_path=f.name)
        elif to_language == 'en':
            tts = TTS(model_name="tts_models/en/jenny/jenny")
            tts.tts_to_file(text=text, file_path=f.name)
        elif to_language == 'es':
            tts = TTS(model_name="tts_models/es/css10/vits")
            tts.tts_to_file(text=text,
                            file_path=f.name)
        else:
            raise Exception("Language not supported")

        # FOR TESTING
        # os.system("afplay " + f.name)

    with open(f.name, 'rb') as file:
        audio_data = file.read()
    os.unlink(f.name)

    return (audio_data, f.name)
