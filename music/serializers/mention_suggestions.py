from django.contrib.auth import get_user_model
from rest_framework import serializers


User = get_user_model()


class MentionSuggestionSerializer(serializers.ModelSerializer):
    """
    Lightweight public user data for mention autocomplete.
    """

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "display_name",
            "profile_image",
            "is_verified",
            "is_identity_verified",
        ]
        read_only_fields = fields