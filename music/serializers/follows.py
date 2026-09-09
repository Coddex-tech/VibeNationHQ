from rest_framework import serializers

from music.models import (
    ArtistFollow,
    UserFollow,
    Artist,
)

from .base import BaseModelSerializer
from .catalog import ArtistCardSerializer


# ============================================================
# ARTIST FOLLOW
# ============================================================

class ArtistFollowSerializer(BaseModelSerializer):
    """
    Read-only representation of a user following an artist.
    """

    artist = ArtistCardSerializer(
        read_only=True,
    )

    class Meta:
        model = ArtistFollow
        fields = [
            "id",
            "user",
            "artist",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class ArtistFollowCreateSerializer(serializers.ModelSerializer):
    """
    Create a follow relationship between the authenticated user
    and an Artist catalog entity.

    Artists are catalog entities and do not have user accounts.
    The authenticated user is assigned server-side.
    """

    artist = serializers.PrimaryKeyRelatedField(
        queryset=Artist.objects.filter(
            is_active=True,
        )
    )

    class Meta:
        model = ArtistFollow
        fields = [
            "artist",
        ]

    def create(self, validated_data):
        request = self.context["request"]

        return ArtistFollow.objects.create(
            user=request.user,
            **validated_data,
        )


# ============================================================
# USER FOLLOW
# ============================================================

class UserFollowSerializer(BaseModelSerializer):
    """
    Read-only representation of a user-to-user follow relationship.
    """

    class Meta:
        model = UserFollow
        fields = [
            "id",
            "follower",
            "following",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class UserFollowCreateSerializer(serializers.ModelSerializer):
    """
    Create a user-to-user follow relationship.

    The authenticated user becomes the follower.
    The target user is supplied by the client.

    Self-following is prevented by the model constraint.
    """

    following = serializers.PrimaryKeyRelatedField(
        queryset=UserFollow._meta.get_field(
            "following"
        ).remote_field.model.objects.all()
    )

    class Meta:
        model = UserFollow
        fields = [
            "following",
        ]

    def create(self, validated_data):
        request = self.context["request"]

        return UserFollow.objects.create(
            follower=request.user,
            **validated_data,
        )