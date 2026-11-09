from django.contrib.auth import get_user_model
from rest_framework import serializers

from music.models import (
    ArtistFollow,
    UserFollow,
)


User = get_user_model()


class PublicProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for publicly visible VibeNation user profiles.
    """

    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    artists_count = serializers.SerializerMethodField()

    is_following = serializers.SerializerMethodField()
    is_following_you = serializers.SerializerMethodField()
    
    is_own_profile = serializers.SerializerMethodField()

    profile_image = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "display_name",
            "bio",
            "profile_image",
            "is_verified",
            "is_identity_verified",
            "followers_count",
            "following_count",
            "artists_count",
            "is_following",
            "is_following_you",
            "is_own_profile",
            "date_joined",
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

    def get_followers_count(self, obj):
        return UserFollow.objects.filter(
            following=obj,
        ).count()

    def get_following_count(self, obj):
        return UserFollow.objects.filter(
            follower=obj,
        ).count()

    def get_artists_count(self, obj):
        return ArtistFollow.objects.filter(
            user=obj,
        ).count()

    def get_is_following(self, obj):
        request = self.context.get("request")

        if request is None:
            return False

        viewer = request.user

        if not viewer or not viewer.is_authenticated:
            return False

        if viewer.pk == obj.pk:
            return False

        return UserFollow.objects.filter(
            follower=viewer,
            following=obj,
        ).exists()

    def get_is_following_you(self, obj):
        request = self.context.get("request")

        if request is None:
            return False

        viewer = request.user

        if not viewer or not viewer.is_authenticated:
            return False

        if viewer.pk == obj.pk:
            return False

        return UserFollow.objects.filter(
            follower=obj,
            following=viewer,
        ).exists()

    def get_is_own_profile(self, obj):
        request = self.context.get("request")

        if request is None:
            return False

        viewer = request.user

        return (
            viewer.is_authenticated
            and viewer.pk == obj.pk
        )