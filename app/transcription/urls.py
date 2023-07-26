from django.urls import path, include

from .views import index, processAudio
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'process', processAudio, basename="process")

app_name = 'transcription'

urlpatterns = [
    path('', index),
    path('api/', include(router.urls)),
]
