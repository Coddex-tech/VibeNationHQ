from __future__ import annotations

from rest_framework import serializers

from .community import CommunityPostSerializer
from .editorial import EditorialArticleCardSerializer


class MusicFeedItemSerializer(serializers.Serializer):
    """
    Serializes one item in the mixed music feed.

    Supported feed items:
    - Community posts
    - Editorial articles

    The feed service handles candidate generation, ranking,
    personalization, diversity, mixing, and pagination.

    This serializer only converts selected candidates into
    their public representations.
    """

    content_type = serializers.CharField(
        read_only=True,
    )

    source = serializers.CharField(
        read_only=True,
    )

    content = serializers.SerializerMethodField()

    def get_content(self, candidate):
        if candidate.content_type == "community_post":
            return CommunityPostSerializer(
                candidate.object,
                context=self.context,
            ).data

        if candidate.content_type == "editorial":
            return EditorialArticleCardSerializer(
                candidate.object,
                context=self.context,
            ).data

        return None

    def to_representation(self, candidate):
        return {
            "content_type": candidate.content_type,
            "source": candidate.source,
            "content": self.get_content(candidate),
        }


class MusicFeedSerializer(serializers.Serializer):
    """
    Public response serializer for the mixed music feed endpoint.
    """

    results = MusicFeedItemSerializer(
        many=True,
        read_only=True,
    )

    has_more = serializers.BooleanField(
        read_only=True,
    )

    next_cursor = serializers.CharField(
        read_only=True,
        allow_null=True,
    )