from __future__ import annotations

from rest_framework import serializers

from .catalog import (
    AlbumCardSerializer,
    ArtistCardSerializer,
    SongCardSerializer,
)
from .community import CommunityPostSerializer


class MusicFeedItemSerializer(serializers.Serializer):
    """
    Serializes one heterogeneous item in the music feed.

    The feed service decides which object belongs in the feed;
    this serializer only converts that object into its public
    representation.
    """

    content_type = serializers.CharField(
        read_only=True,
    )

    source = serializers.CharField(
        read_only=True,
    )

    content = serializers.SerializerMethodField()

    def get_content(self, candidate):
        content_type = candidate.content_type
        obj = candidate.object

        if content_type == "community_post":
            return CommunityPostSerializer(
                obj,
                context=self.context,
            ).data

        if content_type == "editorial":
            return self._serialize_editorial(obj)

        if content_type == "song":
            return SongCardSerializer(
                obj,
                context=self.context,
            ).data

        if content_type == "album":
            return AlbumCardSerializer(
                obj,
                context=self.context,
            ).data

        if content_type == "artist":
            artist_data = ArtistCardSerializer(
                obj,
                context=self.context,
            ).data

            artist_data["is_following"] = bool(
                getattr(obj, "is_following", False)
            )

            return artist_data

        return None

    def _serialize_editorial(self, obj):
        """
        Keep the feed editorial representation lightweight.

        We intentionally do not use EditorialArticleCardSerializer
        here because its `liked` field depends on
        `user_has_liked`, which would require additional query
        handling for feed-sized result sets.
        """
        author = obj.author

        full_name = author.get_full_name().strip()

        if full_name:
            author_name = full_name
        else:
            author_name = (
                getattr(author, "username", None)
                or getattr(author, "email", "")
            )

        song = None

        if obj.song is not None:
            song = SongCardSerializer(
                obj.song,
                context=self.context,
            ).data

        artist = None

        if obj.artist is not None:
            artist = ArtistCardSerializer(
                obj.artist,
                context=self.context,
            ).data

        album = None

        if obj.album is not None:
            album = AlbumCardSerializer(
                obj.album,
                context=self.context,
            ).data

        return {
            "id": obj.id,
            "title": obj.title,
            "slug": obj.slug,
            "excerpt": obj.excerpt,
            "author": {
                "id": obj.author_id,
                "name": author_name,
            },
            "song": song,
            "artist": artist,
            "album": album,
            "status": obj.status,
            "published_at": obj.published_at,
            "is_featured": obj.is_featured,
            "views_count": obj.views_count,
            "likes_count": obj.likes_count,
            "comments_count": obj.comments_count,
        }

    def to_representation(self, candidate):
        return {
            "content_type": candidate.content_type,
            "source": candidate.source,
            "content": self.get_content(candidate),
        }


class MusicFeedSerializer(serializers.Serializer):
    """
    Public response serializer for the music feed endpoint.
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