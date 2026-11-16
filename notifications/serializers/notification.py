from rest_framework import serializers

from notifications.models import Notification
from django.contrib.auth import get_user_model


User = get_user_model()


class NotificationActorSerializer(serializers.ModelSerializer):
    """
    Lightweight public user representation for notification actors.

    Deliberately excludes follow-status fields because the
    notification list does not need them.
    """

    profile_image = serializers.SerializerMethodField()

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

    def get_profile_image(self, obj):
        request = self.context.get("request")

        if not obj.profile_image:
            return None

        image_url = obj.profile_image.url

        if request is not None:
            return request.build_absolute_uri(image_url)

        return image_url


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializes a notification-centre item.

    Actors must be supplied through an optimized queryset
    prefetch using the `latest_active_events` attribute.

    This serializer deliberately does not execute additional
    database queries to retrieve notification actors.
    """

    is_read = serializers.BooleanField(read_only=True)

    target = serializers.SerializerMethodField()
    actors = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            "id",
            "category",
            "notification_type",
            "metadata",
            "target",
            "event_count",
            "is_read",
            "read_at",
            "actors",
            "latest_event_at",
            "created_at",
        ]
        read_only_fields = fields

    def get_target(self, obj):
        if (
            obj.target_content_type_id is None
            or obj.target_object_id is None
        ):
            return None

        return {
            "app_label": obj.target_content_type.app_label,
            "model": obj.target_content_type.model,
            "object_id": obj.target_object_id,
        }

    def get_actors(self, obj):
        events = getattr(
            obj,
            "latest_active_events",
            None,
        )

        if events is None:
            return []

        actors = [
            event.actor
            for event in events
            if event.actor is not None
        ]

        return NotificationActorSerializer(
            actors,
            many=True,
            context=self.context,
        ).data