from rest_framework import serializers

from music.models import (
    EditorialArticleLike,
    CommunityPostLike,
    EditorialCommentLike,
    CommunityPostCommentLike,
)

from .base import BaseModelSerializer


# ============================================================
# EDITORIAL ARTICLE LIKE
# ============================================================

class EditorialArticleLikeSerializer(BaseModelSerializer):
    """
    Read-only representation of a user's like on an
    editorial article.
    """

    class Meta:
        model = EditorialArticleLike
        fields = [
            "id",
            "user",
            "article",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class EditorialArticleLikeCreateSerializer(
    serializers.ModelSerializer
):
    """
    Create a like for an editorial article.

    The authenticated user and target article are assigned
    server-side. The article comes from the URL.
    """

    class Meta:
        model = EditorialArticleLike
        fields = []


# ============================================================
# COMMUNITY POST LIKE
# ============================================================

class CommunityPostLikeSerializer(BaseModelSerializer):
    """
    Read-only representation of a user's like on a
    community post.
    """

    class Meta:
        model = CommunityPostLike
        fields = [
            "id",
            "user",
            "post",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class CommunityPostLikeCreateSerializer(
    serializers.ModelSerializer
):
    """
    Create a like for a community post.

    The authenticated user and target post are assigned
    server-side. The post comes from the URL.
    """

    class Meta:
        model = CommunityPostLike
        fields = []


# ============================================================
# EDITORIAL COMMENT LIKE
# ============================================================

class EditorialCommentLikeSerializer(BaseModelSerializer):
    """
    Read-only representation of a user's like on an
    editorial comment or reply.
    """

    class Meta:
        model = EditorialCommentLike
        fields = [
            "id",
            "user",
            "comment",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class EditorialCommentLikeCreateSerializer(
    serializers.ModelSerializer
):
    """
    Create a like for an editorial comment or reply.

    The authenticated user and target comment are assigned
    server-side. The comment comes from the URL.
    """

    class Meta:
        model = EditorialCommentLike
        fields = []


# ============================================================
# COMMUNITY POST COMMENT LIKE
# ============================================================

class CommunityPostCommentLikeSerializer(
    BaseModelSerializer
):
    """
    Read-only representation of a user's like on a
    community post comment or reply.
    """

    class Meta:
        model = CommunityPostCommentLike
        fields = [
            "id",
            "user",
            "comment",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class CommunityPostCommentLikeCreateSerializer(
    serializers.ModelSerializer
):
    """
    Create a like for a community post comment or reply.

    The authenticated user and target comment are assigned
    server-side. The comment comes from the URL.
    """

    class Meta:
        model = CommunityPostCommentLike
        fields = []