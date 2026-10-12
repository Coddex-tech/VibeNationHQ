from rest_framework import serializers


class GoogleLoginSerializer(serializers.Serializer):
    credential = serializers.CharField(
        required=True,
        allow_blank=False,
        trim_whitespace=True,
    )