from rest_framework import serializers

from music.models import (
    EditorialArticleLike,
    CommunityPostLike,
    EditorialCommentLike,
    CommunityPostCommentLike,
    EditorialArticle,
    CommunityPost,
    EditorialComment,
    CommunityPostComment,
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


class EditorialArticleLikeCreateSerializer(serializers.ModelSerializer):
    """
    Create a like for an editorial article.

    The authenticated user is assigned server-side.
    Only published articles can be liked.
    """

    article = serializers.PrimaryKeyRelatedField(
        queryset=EditorialArticle.objects.filter(
            status=EditorialArticle.Status.PUBLISHED,
        )
    )

    class Meta:
        model = EditorialArticleLike
        fields = [
            "article",
        ]

    def create(self, validated_data):
        request = self.context["request"]

        return EditorialArticleLike.objects.create(
            user=request.user,
            **validated_data,
        )


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


class CommunityPostLikeCreateSerializer(serializers.ModelSerializer):
    """
    Create a like for a community post.

    The authenticated user is assigned server-side.
    Only published posts can be liked.
    """

    post = serializers.PrimaryKeyRelatedField(
        queryset=CommunityPost.objects.filter(
            status=CommunityPost.Status.PUBLISHED,
        )
    )

    class Meta:
        model = CommunityPostLike
        fields = [
            "post",
        ]

    def create(self, validated_data):
        request = self.context["request"]

        return CommunityPostLike.objects.create(
            user=request.user,
            **validated_data,
        )


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


class EditorialCommentLikeCreateSerializer(serializers.ModelSerializer):
    """
    Create a like for an editorial comment or reply.

    The authenticated user is assigned server-side.
    The comment must belong to an editorial article that
    is currently published.
    """

    comment = serializers.PrimaryKeyRelatedField(
        queryset=EditorialComment.objects.filter(
            status=EditorialComment.Status.PUBLISHED,
            article__status=EditorialArticle.Status.PUBLISHED,
        )
    )

    class Meta:
        model = EditorialCommentLike
        fields = [
            "comment",
        ]

    def create(self, validated_data):
        request = self.context["request"]

        return EditorialCommentLike.objects.create(
            user=request.user,
            **validated_data,
        )


# ============================================================
# COMMUNITY POST COMMENT LIKE
# ============================================================

class CommunityPostCommentLikeSerializer(BaseModelSerializer):
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

    The authenticated user is assigned server-side.
    The comment must belong to a currently published post.
    """

    comment = serializers.PrimaryKeyRelatedField(
        queryset=CommunityPostComment.objects.filter(
            status=CommunityPostComment.Status.PUBLISHED,
            post__status=CommunityPost.Status.PUBLISHED,
        )
    )

    class Meta:
        model = CommunityPostCommentLike
        fields = [
            "comment",
        ]

    def create(self, validated_data):
        request = self.context["request"]

        return CommunityPostCommentLike.objects.create(
            user=request.user,
            **validated_data,
        )