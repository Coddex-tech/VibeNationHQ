from rest_framework import serializers
from django.conf import settings
from django.urls import reverse
from .models import Song, Artist, MusicComment, Album
from utils.date_time_extra import format_hybrid_time

class ArtistSerializer(serializers.ModelSerializer):
    """
    Compact Artist serializer for nested API responses.
    """

    class Meta:
        model = Artist

        fields = (
            "id",
            "name",
            "bio",
        )

class ArtistCardSerializer(serializers.ModelSerializer):
    """
    Compact Artist serializer for nested API responses.
    """

    class Meta:
        model = Artist

        fields = (
            "id",
            "name",
        )

class GenreSerializer(serializers.Serializer):
    """
    Compact Genre serializer.
    """

    id = serializers.IntegerField()
    name = serializers.CharField()
    slug = serializers.CharField()


class TagSerializer(serializers.Serializer):
    """
    Compact Tag serializer.
    """

    id = serializers.IntegerField()
    name = serializers.CharField()
    slug = serializers.CharField()
    url = serializers.URLField()


class SeoSerializer(serializers.Serializer):
    """
    SEO/OpenGraph serializer.
    """

    title = serializers.CharField()
    description = serializers.CharField()
    image = serializers.URLField()
    url = serializers.URLField()


# ============ NEW OPTIMIZING ================
class MusicReplySerializer(serializers.ModelSerializer):
    """
    Serializes a flattened reply node.
    """

    friendly_date = serializers.SerializerMethodField()
    display_name = serializers.CharField(read_only=True)
    is_verified_staff = serializers.BooleanField(read_only=True)
    replying_to = serializers.CharField(read_only=True)

    class Meta:
        model = MusicComment
        fields = [
            "id",
            "parent_id",
            "display_name",
            "content",
            "friendly_date",
            "is_verified_staff",
            "replying_to",
        ]

    def get_friendly_date(self, obj):
        return format_hybrid_time(obj.created_at)


class MusicCommentSerializer(serializers.ModelSerializer):
    """
    Root comment serializer.
    """

    friendly_date = serializers.SerializerMethodField()
    display_name = serializers.CharField(read_only=True)
    is_verified_staff = serializers.BooleanField(read_only=True)

    replies = serializers.SerializerMethodField()
    total_replies_count = serializers.SerializerMethodField()

    class Meta:
        model = MusicComment
        fields = [
            "id",
            "display_name",
            "content",
            "friendly_date",
            "is_verified_staff",
            "replies",
            "total_replies_count",
        ]

    def get_friendly_date(self, obj):
        return format_hybrid_time(obj.created_at)

    def get_replies(self, obj):
        initial_batch = obj.get_all_replies()[:settings.MUSIC_INITIAL_REPLIES]

        return MusicReplySerializer(
            initial_batch,
            many=True
        ).data

    def get_total_replies_count(self, obj):
        return len(obj.get_all_replies())
