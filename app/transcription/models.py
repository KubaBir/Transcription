from django.db import models

# Create your models here.


class AudioFile(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    file = models.FileField()
