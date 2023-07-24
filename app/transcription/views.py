from django.shortcuts import render

import whisper
import tempfile
import os


def index(request):
    if request.method == "POST":
        file = request.FILES["audio"]

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

    return render(request, "transcription/index.html")
