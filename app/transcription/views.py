from django.shortcuts import render
# from app.tasks import compute

from .serializers import AudioSerializer
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
import tempfile
import os
import whisper


def index(request):
    # if request.method == "POST":
    #     file = request.FILES.get("medium")
    #     if file:
    #         compute.delay(file.read())
    return render(request, "transcription/index.html")


class processAudio(ViewSet):
    serializer_class = AudioSerializer

    def create(self, request):
        file = request.FILES["audio"]
        if not file:
            return Response("No file provided", status=status.HTTP_400_BAD_REQUEST)

        with tempfile.NamedTemporaryFile(suffix=os.path.splitext(file.name)[1], delete=False) as f:
            for chunk in file.chunks():
                f.write(chunk)
            f.seek(0)
        try:
            model = whisper.load_model("base")
            result = model.transcribe(f.name)
            print(result["text"])

        finally:
            os.unlink(f.name)
        return Response(result["text"], status=status.HTTP_200_OK)
