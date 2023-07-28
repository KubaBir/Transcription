from django.urls import path

from . import views

app_name = 'live_services'

urlpatterns = [
    path("", views.index, name="index"),
]
