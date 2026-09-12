from rest_framework import serializers

from ..models import UserSession


class UserSessionSerializer(serializers.ModelSerializer):
    is_current = serializers.SerializerMethodField()

    class Meta:
        model = UserSession
        fields = [
            "id",
            "device_name",
            "user_agent",
            "ip_address",
            "created_at",
            "last_seen_at",
            "expires_at",
            "is_current",
        ]
        read_only_fields = fields

    def get_is_current(self, obj):
        current_session = self.context.get(
            "current_session"
        )

        return (
            current_session is not None
            and obj.id == current_session.id
        )