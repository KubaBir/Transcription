from rest_framework import serializers


class AudioSerializer(serializers.Serializer):
    audio = serializers.FileField()

    class Meta:
        fields = ['audio']
