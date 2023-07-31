from django.urls import path, include

from .views import index, TranscriptionView, getAudioResponseView, commandView, TranslationView, ChatPromptView
from rest_framework import routers

app_name = 'transcription'

urlpatterns = [
    path('', index),
    path('api/transcribe/', TranscriptionView.as_view(), name='transcribe'),
    path('api/voiceover/', getAudioResponseView.as_view(), name='voiceover'),
    path('api/command/', commandView.as_view(), name='command'),
    path('api/translate/', TranslationView.as_view(), name='translate'),
    path('api/chat/', ChatPromptView.as_view(), name='chat'),
]
