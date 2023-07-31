from django.urls import path, include

from .views import index, TranscriptionView, getAudioResponse, commandView, TranslationView
from rest_framework import routers

app_name = 'transcription'

urlpatterns = [
    path('', index),
    path('api/transcribe/', TranscriptionView.as_view(), name='transcribe'),
    path('api/voiceover/', getAudioResponse.as_view(), name='voiceover'),
    path('api/command/', commandView.as_view(), name='command'),
    path('api/translate/', TranslationView.as_view(), name='translate'),
]
