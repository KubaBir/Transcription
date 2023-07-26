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


def index(request):
    return render(request, "transcription/index.html")


class processAudio(ViewSet):
    serializer_class = AudioSerializer

    def create(self, request):
        print("Got a request")
        file = request.FILES["audio"]
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
            _, probs = model.detect_language(mel)
            options = whisper.DecodingOptions(fp16=False)
            translated = ""
            lang = max(probs, key=probs.get)
            if lang != 'en':
                translated = whisper.decode(
                    model, mel, options, task='translate').text
            original = whisper.decode(model, mel, options).text

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
        print(request.data)
        audio_file_path = generate_tts(request.data['prompt'])

        with open(audio_file_path, 'rb') as file:
            audio_data = file.read()

        response = HttpResponse(audio_data, content_type='audio/wav')
        response['Content-Disposition'] = f'attachment; filename={audio_file_path}'

        return response


def generate_tts(text, lang='pl'):
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
        if lang == 'pl':
            tts = TTS(model_name="tts_models/pl/mai_female/vits")
            tts.tts_to_file(text=text,
                            file_path=f.name)
        else:
            tts = TTS(model_name="tts_models/multilingual/multi-dataset/your_tts")
            tts.tts_to_file(text=text,
                            speaker=tts.speakers[4],
                            language=tts.languages[0],
                            file_path=f.name)
        # FOR TESTING
        # os.system("afplay " + f.name)
    return f.name
