from rest_framework import serializers

from music.models import (
    Genre,
    Artist,
    Album,
    AlbumTrack,
    Song,
)

from .base import BaseModelSerializer


# ============================================================
# GENRE
# ============================================================

class GenreSerializer(BaseModelSerializer):
    """
    Basic representation of a music genre.
    """

    class Meta:
        model = Genre
        fields = [
            "id",
            "name",
            "slug",
            "description",
        ]
        read_only_fields = fields


# ============================================================
# ARTIST
# ============================================================

class ArtistCardSerializer(BaseModelSerializer):
    """
    Lightweight artist representation.

    Used when an artist is displayed inside:
    - song cards
    - album cards
    - search results
    - lists
    """

    class Meta:
        model = Artist
        fields = [
            "id",
            "name",
            "slug",
            "profile_image",
            "is_verified",
            "followers_count",
        ]
        read_only_fields = fields


class ArtistSerializer(BaseModelSerializer):
    """
    Full artist representation.
    """

    class Meta:
        model = Artist
        fields = [
            "id",
            "name",
            "slug",
            "bio",
            "profile_image",
            "banner_image",
            "country",
            "website_url",
            "instagram_url",
            "x_url",
            "youtube_url",
            "spotify_url",
            "apple_music_url",
            "is_verified",
            "followers_count",
        ]
        read_only_fields = fields


# ============================================================
# ALBUM
# ============================================================

class AlbumCardSerializer(BaseModelSerializer):
    """
    Lightweight album representation.

    Designed for album cards, lists, search results,
    and other places where the complete album object
    is unnecessary.
    """

    artists = ArtistCardSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Album
        fields = [
            "id",
            "title",
            "slug",
            "artists",
            "release_type",
            "artwork",
            "release_date",
            "favorites_count",
            "ratings_count",
        ]
        read_only_fields = fields


# ============================================================
# SONG
# ============================================================

class SongCardSerializer(BaseModelSerializer):
    """
    Lightweight song representation.

    Designed for:
    - homepage song cards
    - trending songs
    - search results
    - recommendation lists
    - community music selection results
    """

    artists = ArtistCardSerializer(
        many=True,
        read_only=True,
    )

    featured_artists = ArtistCardSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Song
        fields = [
            "id",
            "title",
            "slug",
            "artists",
            "featured_artists",
            "artwork",
            "release_date",
            "duration_seconds",
            "duration_display",
            "favorites_count",
            "ratings_count",
        ]
        read_only_fields = fields


class SongSerializer(BaseModelSerializer):
    """
    Standard song representation.

    Provides more information than SongCardSerializer
    without unnecessarily loading unrelated resources.
    """

    artists = ArtistCardSerializer(
        many=True,
        read_only=True,
    )

    featured_artists = ArtistCardSerializer(
        many=True,
        read_only=True,
    )

    genres = GenreSerializer(
        many=True,
        read_only=True,
    )

    album = AlbumCardSerializer(
        read_only=True,
    )

    class Meta:
        model = Song
        fields = [
            "id",
            "title",
            "slug",
            "artists",
            "featured_artists",
            "album",
            "genres",
            "artwork",
            "release_date",
            "duration_seconds",
            "duration_display",
            "description",

            # Editorial scoring
            "editorial_review",
            "editorial_score",
            "production_score",
            "lyrics_score",
            "vocals_score",
            "replay_score",
            "cultural_impact_score",

            # Official listening destinations
            "spotify_url",
            "apple_music_url",
            "youtube_url",
            "audiomack_url",
            "boomplay_url",

            # Publication information
            "published_at",
            "is_featured",

            # Engagement counters
            "favorites_count",
            "ratings_count",
        ]
        read_only_fields = fields


# ============================================================
# ALBUM TRACK
# ============================================================

class AlbumTrackSerializer(BaseModelSerializer):
    """
    Represents a song's position inside an album.
    """

    song = SongCardSerializer(
        read_only=True,
    )

    class Meta:
        model = AlbumTrack
        fields = [
            "id",
            "track_number",
            "song",
        ]
        read_only_fields = fields


# ============================================================
# ALBUM
# ============================================================

class AlbumSerializer(BaseModelSerializer):
    """
    Standard album representation.
    """

    artists = ArtistCardSerializer(
        many=True,
        read_only=True,
    )

    tracks = serializers.SerializerMethodField()

    class Meta:
        model = Album
        fields = [
            "id",
            "title",
            "slug",
            "artists",
            "release_type",
            "artwork",
            "release_date",
            "description",

            # Editorial
            "editorial_review",
            "editorial_score",

            # Official listening destinations
            "spotify_url",
            "apple_music_url",
            "youtube_url",
            "audiomack_url",
            "boomplay_url",

            # Publication
            "published_at",
            "is_featured",

            # Engagement
            "favorites_count",
            "ratings_count",

            # Tracklist
            "tracks",
        ]
        read_only_fields = fields

    def get_tracks(self, obj):
        tracks = obj.tracklist.select_related(
            "song"
        ).prefetch_related(
            "song__artists",
            "song__featured_artists",
        )

        return AlbumTrackSerializer(
            tracks,
            many=True,
            context=self.context,
        ).data