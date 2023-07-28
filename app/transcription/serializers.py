from rest_framework import serializers


class AudioSerializer(serializers.Serializer):
    audio = serializers.FileField(required=True)
    to_language = serializers.CharField(max_length=255)

    class Meta:
        fields = ['audio', 'to_language']


class TTSSerializer(serializers.Serializer):
    prompt = serializers.CharField(max_length=255)
    to_language = serializers.CharField(max_length=255)

    class Meta:
        fields = '__all__'
