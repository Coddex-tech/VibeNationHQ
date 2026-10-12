from __future__ import annotations

from rest_framework import serializers

from music.models import (
    EditorialArticle,
    EditorialArticleReport,
    EditorialComment,
    EditorialCommentReport,
)

from .base import BaseModelSerializer
from .catalog import (
    AlbumCardSerializer,
    ArtistCardSerializer,
    GenreSerializer,
    SongCardSerializer,
)


# ============================================================
# EDITORIAL ARTICLE
# ============================================================


class EditorialArticleCardSerializer(BaseModelSerializer):
    """
    Lightweight serializer for editorial article listings,
    homepage sections, and related-content cards.
    """

    author = serializers.SerializerMethodField()

    song = SongCardSerializer(
        read_only=True,
    )

    artist = ArtistCardSerializer(
        read_only=True,
    )

    album = AlbumCardSerializer(
        read_only=True,
    )

    liked = serializers.BooleanField(
        source="user_has_liked",
        read_only=True,
        default=False,
    )

    class Meta:
        model = EditorialArticle
        fields = [
            "id",
            "title",
            "slug",
            "excerpt",
            "author",
            "song",
            "artist",
            "album",
            "status",
            "published_at",
            "is_featured",
            "views_count",
            "likes_count",
            "liked",
            "comments_count",
        ]
        read_only_fields = fields

    def get_author(self, obj):
        return {
            "id": obj.author_id,
            "name": self._get_user_display_name(
                obj.author,
            ),
        }

    @staticmethod
    def _get_user_display_name(user):
        full_name = user.get_full_name().strip()

        if full_name:
            return full_name

        return (
            getattr(user, "username", None)
            or getattr(user, "email", "")
        )


class EditorialArticleSerializer(
    BaseModelSerializer,
):
    """
    Full public serializer for an editorial article.
    """

    author = serializers.SerializerMethodField()

    song = SongCardSerializer(
        read_only=True,
    )

    artist = ArtistCardSerializer(
        read_only=True,
    )

    album = AlbumCardSerializer(
        read_only=True,
    )

    genres = GenreSerializer(
        many=True,
        read_only=True,
    )

    liked = serializers.BooleanField(
        source="user_has_liked",
        read_only=True,
        default=False,
    )

    class Meta:
        model = EditorialArticle
        fields = [
            "id",
            "title",
            "slug",
            "excerpt",
            "content",
            "author",
            "song",
            "artist",
            "album",
            "genres",
            "status",
            "published_at",
            "is_featured",
            "views_count",
            "likes_count",
            "liked",
            "comments_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_author(self, obj):
        return {
            "id": obj.author_id,
            "name": self._get_user_display_name(
                obj.author,
            ),
        }

    @staticmethod
    def _get_user_display_name(user):
        full_name = user.get_full_name().strip()

        if full_name:
            return full_name

        return (
            getattr(user, "username", None)
            or getattr(user, "email", "")
        )


# ============================================================
# EDITORIAL COMMENT
# ============================================================


class EditorialCommentSerializer(
    BaseModelSerializer,
):
    """
    Read-only serializer for published editorial comments
    and replies.
    """

    user = serializers.SerializerMethodField()

    liked = serializers.BooleanField(
        source="user_has_liked",
        read_only=True,
        default=False,
    )

    class Meta:
        model = EditorialComment
        fields = [
            "id",
            "user",
            "article",
            "parent",
            "content",
            "views_count",
            "likes_count",
            "liked",
            "replies_count",
            "status",
            "is_edited",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_user(self, obj):
        return {
            "id": obj.user_id,
            "name": self._get_user_display_name(
                obj.user,
            ),
        }

    @staticmethod
    def _get_user_display_name(user):
        full_name = user.get_full_name().strip()

        if full_name:
            return full_name

        return (
            getattr(user, "username", None)
            or getattr(user, "email", "")
        )


class EditorialCommentCreateSerializer(
    BaseModelSerializer,
):
    """
    Serializer for creating an editorial comment or reply.

    The article is taken from the URL and the authenticated
    user is assigned by the service layer.
    """

    class Meta:
        model = EditorialComment
        fields = [
            "parent",
            "content",
        ]

    def validate_content(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Comment cannot be empty."
            )

        return value


class EditorialCommentUpdateSerializer(
    BaseModelSerializer,
):
    """
    Serializer for editing an editorial comment.
    """

    class Meta:
        model = EditorialComment
        fields = [
            "content",
        ]

    def validate_content(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Comment cannot be empty."
            )

        return value


# ============================================================
# EDITORIAL ARTICLE REPORT
# ============================================================


class EditorialArticleReportSerializer(
    BaseModelSerializer,
):
    """
    Read-only serializer for an article report.
    """

    class Meta:
        model = EditorialArticleReport
        fields = [
            "id",
            "user",
            "article",
            "reason",
            "details",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class EditorialArticleReportCreateSerializer(
    BaseModelSerializer,
):
    """
    Serializer for submitting an article report.

    The authenticated user and article are assigned by
    the API/service layer.
    """

    class Meta:
        model = EditorialArticleReport
        fields = [
            "reason",
            "details",
        ]

    def validate_details(self, value):
        return value.strip()


# ============================================================
# EDITORIAL COMMENT REPORT
# ============================================================


class EditorialCommentReportSerializer(
    BaseModelSerializer,
):
    """
    Read-only serializer for an editorial comment report.
    """

    class Meta:
        model = EditorialCommentReport
        fields = [
            "id",
            "user",
            "comment",
            "reason",
            "details",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class EditorialCommentReportCreateSerializer(
    BaseModelSerializer,
):
    """
    Serializer for submitting an editorial comment report.

    The authenticated user and comment are assigned by
    the API/service layer.
    """

    class Meta:
        model = EditorialCommentReport
        fields = [
            "reason",
            "details",
        ]

    def validate_details(self, value):
        return value.strip()