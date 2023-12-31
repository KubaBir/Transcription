import os
import tempfile
import openai

import translators as tr
import whisper
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.views import APIView
from torch import cuda
from TTS.api import TTS

from .serializers import AudioSerializer, TTSSerializer, TranslationSerializer, ChatSerializer


def index(request):
    return render(request, "transcription/index.html")


class commandView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    supported_languages = {
        'pl': 0,
        'en': 0,
        'es': 0,
    }

    def get_serializer(self, *args, **kwargs):
        return AudioSerializer(*args, **kwargs)

    def post(self, request):
        prompts = {
            'pl': 'czytaj, przeczytaj, tłumacz, przetłumacz',
            'en': 'read, translate',
            'es': 'leer, traducir'
        }
        print("Got a command")

        serializer: Serializer = AudioSerializer(data=request.data)
        if serializer.is_valid():
            file = request.FILES["audio"]
            command_language = request.data['to_language']

            f = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            try:
                for chunk in file.chunks():
                    f.write(chunk)
                f.seek(0)

                command = transcribe_from_file(
                    file_path=f.name,
                    model='base',
                    input_lang=command_language,
                    prompt=prompts[command_language])
            finally:
                os.unlink(f.name)

            print(command)

            return process_command(command, command_language)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


def process_command(command, command_language):
    # Translate command to English
    if command_language != 'en':
        command = tr.translate_text(
            command,
            to_language='en',
            from_language=command_language,
            translator='google').lower()
    print(command)

    # Look for keywords
    if 'translat' in command:
        return Response("translate", status.HTTP_200_OK)
    elif 'read' in command:
        return Response("read", status.HTTP_200_OK)
    else:
        return Response("other", status.HTTP_200_OK)


class TranscriptionView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer(self, *args, **kwargs):
        return AudioSerializer(*args, **kwargs)

    def post(self, request):
        print("Got a request")

        serializer: Serializer = AudioSerializer(data=request.data)

        if serializer.is_valid():
            file = request.FILES["audio"]
            to_language = request.data['to_language']

            f = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            try:
                for chunk in file.chunks():
                    f.write(chunk)
                f.seek(0)

                original = transcribe_from_file(f.name, 'small')
                translated = tr.translate_text(
                    original, to_language=to_language, translator='google')
            except:
                return Response("Translation error", status.HTTP_400_BAD_REQUEST)
            finally:
                os.unlink(f.name)

            data = {
                'original': original,
                'translated': translated
            }
            return Response(data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


def transcribe_from_file(file_path, model='base', input_lang=None, prompt=None):
    print(f"Using CUDA: {cuda.is_available()}")
    device = 'cuda' if cuda.is_available() else 'cpu'
    model = whisper.load_model("small").to(device)

    audio = whisper.load_audio(file_path)
    audio = whisper.pad_or_trim(audio)
    mel = whisper.log_mel_spectrogram(audio).to(model.device)
    options = whisper.DecodingOptions(
        fp16=cuda.is_available(),
        language=input_lang,
        prompt=prompt
    )

    res = whisper.decode(model, mel, options).text

    return res


class getAudioResponseView(APIView):

    def get_serializer(self, *args, **kwargs):
        return TTSSerializer(*args, **kwargs)

    def post(self, request, format=None):
        serializer: Serializer = TTSSerializer(data=request.data)
        if serializer.is_valid():
            prompt = serializer.data['prompt']
            language = serializer.data['language']
            audio_data, path = generate_tts(prompt, language)

            response = HttpResponse(audio_data, content_type='audio/wav')
            response['Content-Disposition'] = f'attachment; filename={path}'

            return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def generate_tts(text, language='pl'):
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
        if language == 'pl':
            tts = TTS(model_name="tts_models/pl/mai_female/vits")
            tts.tts_to_file(text=text, file_path=f.name)
        elif language == 'en':
            tts = TTS(model_name="tts_models/en/jenny/jenny")
            tts.tts_to_file(text=text, file_path=f.name)
        elif language == 'es':
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


class TranslationView(APIView):
    def get_serializer(self, *args, **kwargs):
        return TranslationSerializer(*args, **kwargs)

    def post(self, request, format=None):
        serializer: Serializer = TranslationSerializer(data=request.data)
        if serializer.is_valid():
            msg = serializer.data['prompt']
            to_language = serializer.data['to_language']
            from_language = serializer.data.get('from_language', 'auto')

            translation = translate(msg, to_language, from_language)

            data = {
                'original': msg,
                'translation': translation
            }
            return Response(data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def translate(msg, to_language, from_language=None):
    res = tr.translate_text(
        msg,
        to_language=to_language,
        from_language=from_language,
        translator='google')

    return res


class ChatPromptView(APIView):
    def get_serializer(self, *args, **kwargs):
        return ChatSerializer(*args, **kwargs)

    def post(self, request, format=None):
        serializer: Serializer = ChatSerializer(data=request.data)
        if serializer.is_valid():
            messages = serializer.data.get('messages')
            openai.api_key = os.getenv("OPENAI_API_KEY")

            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages)
            chat_response = completion.choices[0].message
            return Response(chat_response, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
