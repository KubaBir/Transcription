# import whisper
# import tempfile
# import os
# from celery import shared_task
# from celery.utils.log import get_task_logger

# logger = get_task_logger(__name__)


# @shared_task
# def test():
#     print("test")
#     return True


# @shared_task
# def compute(bytes):
#     with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
#         f.write(bytes)
#         f.seek(0)
#     try:
#         model = whisper.load_model("base")
#         result = model.transcribe(f.name)
#         print(result["text"])

#     finally:
#         os.unlink(f.name)

#     return True
