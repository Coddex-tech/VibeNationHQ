from django.db.models import Avg, Count, Q
from rest_framework import serializers

from music.models import (
    Album,
    AlbumTrack,
    Artist,
    ArtistFollow,
    CommunityPost,
    CommunityPostTarget,
    Genre,
    Song,
)

from .base import BaseModelSerializer


# ============================================================
# SHARED HELPERS
# ============================================================


def get_community_rating_stats(obj, target_type, target_field):
    """
    Calculate the average rating and rating count from published
    community posts attached to the exact canonical music entity.

    The result is cached on the model instance so requesting both
    serializer fields does not execute the aggregate twice.
    """

    cache_attribute = "_community_rating_stats"

    cached_stats = getattr(obj, cache_attribute, None)

    if cached_stats is not None:
        return cached_stats

    target_filter = {
        f"target__{target_field}_id": obj.pk,
    }

    stats = CommunityPost.objects.filter(
        status=CommunityPost.Status.PUBLISHED,
        target__target_type=target_type,
        rating__isnull=False,
        **target_filter,
    ).aggregate(
        average=Avg("rating"),
        count=Count("rating"),
    )

    result = {
        "average": stats["average"],
        "count": stats["count"] or 0,
    }

    setattr(obj, cache_attribute, result)

    return result


def get_track_community_rating_stats(album):
    """
    Calculate rating statistics from published community posts
    attached to songs included in this album's tracklist.

    These statistics are independent of ratings on posts attached
    directly to the album.

    AlbumTrack is used as the source of track membership so the
    aggregation follows the album's actual tracklist rather than
    relying on the optional Song.album relationship.

    The result is cached on the album instance so the average and
    count serializer fields share one aggregate query.
    """

    cache_attribute = "_track_community_rating_stats"

    cached_stats = getattr(album, cache_attribute, None)

    if cached_stats is not None:
        return cached_stats

    track_song_ids = AlbumTrack.objects.filter(
        album_id=album.pk,
    ).values_list(
        "song_id",
        flat=True,
    )

    stats = CommunityPost.objects.filter(
        status=CommunityPost.Status.PUBLISHED,
        target__target_type=CommunityPostTarget.TargetType.SONG,
        target__song_id__in=track_song_ids,
        rating__isnull=False,
    ).aggregate(
        average=Avg("rating"),
        count=Count("rating"),
    )

    result = {
        "average": stats["average"],
        "count": stats["count"] or 0,
    }

    setattr(album, cache_attribute, result)

    return result


def get_related_community_posts(obj, target_type, target_field, context):
    """
    Return a small collection of recent published community posts
    attached to the exact song, album, or artist.

    Provider identities are prefetched for canonical song targets,
    allowing the existing community serializer to resolve previews.
    """

    from music.serializers.community import CommunityPostSerializer

    target_filter = {
        f"target__{target_field}_id": obj.pk,
    }

    posts = (
        CommunityPost.objects
        .filter(
            status=CommunityPost.Status.PUBLISHED,
            target__target_type=target_type,
            **target_filter,
        )
        .select_related(
            "user",
            "target",
            "target__song",
            "target__album",
            "target__artist",
        )
        .prefetch_related(
            "target__song__artists",
            "target__song__featured_artists",
            "target__song__provider_identities",
            "target__album__artists",
            "target__artist",
        )
        .annotate(
            favorites_count=Count(
                "favorites",
                distinct=True,
            ),
        )
        .order_by("-created_at", "-pk")[:5]
    )

    return CommunityPostSerializer(
        posts,
        many=True,
        context=context,
    ).data


# ============================================================
# GENRE
# ============================================================


class GenreSerializer(BaseModelSerializer):
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
    Artist detail representation.

    Biography, banner, and manually maintained social links are
    intentionally excluded. The detail page must not depend on
    those fields being populated.
    """

    songs = serializers.SerializerMethodField()
    albums = serializers.SerializerMethodField()
    related_posts = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = Artist
        fields = [
            "id",
            "name",
            "slug",
            "profile_image",
            "country",
            "is_verified",
            "followers_count",
            "is_following",
            "songs",
            "albums",
            "related_posts",
        ]
        read_only_fields = fields

    def get_is_following(self, obj):
        request = self.context.get("request")

        if not request or not request.user.is_authenticated:
            return False

        return ArtistFollow.objects.filter(
            user=request.user,
            artist=obj,
        ).exists()

    def get_songs(self, obj):
        """
        Return recent published songs where this artist is either
        a primary artist or a featured artist.
        """

        songs = (
            Song.objects
            .filter(
                status=Song.Status.PUBLISHED,
            )
            .filter(
                Q(artists=obj) | Q(featured_artists=obj),
            )
            .select_related("album")
            .prefetch_related(
                "artists",
                "featured_artists",
                "genres",
            )
            .distinct()
            .order_by("-published_at", "-pk")[:12]
        )

        return SongCardSerializer(
            songs,
            many=True,
            context=self.context,
        ).data

    def get_albums(self, obj):
        """
        Return recent published albums associated with this artist.
        """

        albums = (
            Album.objects
            .filter(
                status=Album.Status.PUBLISHED,
                artists=obj,
            )
            .prefetch_related("artists")
            .order_by("-published_at", "-pk")[:12]
        )

        return AlbumCardSerializer(
            albums,
            many=True,
            context=self.context,
        ).data

    def get_related_posts(self, obj):
        return get_related_community_posts(
            obj=obj,
            target_type=CommunityPostTarget.TargetType.ARTIST,
            target_field="artist",
            context=self.context,
        )


# ============================================================
# ALBUM CARD
# ============================================================


class AlbumCardSerializer(BaseModelSerializer):
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
# SONG CARD
# ============================================================


class SongCardSerializer(BaseModelSerializer):
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


# ============================================================
# SONG DETAIL
# ============================================================


class SongSerializer(BaseModelSerializer):
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

    preview_url = serializers.SerializerMethodField()
    community_rating_average = serializers.SerializerMethodField()
    community_rating_count = serializers.SerializerMethodField()
    related_posts = serializers.SerializerMethodField()

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
            "editorial_review",
            "editorial_score",
            "production_score",
            "lyrics_score",
            "vocals_score",
            "replay_score",
            "cultural_impact_score",
            "spotify_url",
            "apple_music_url",
            "youtube_url",
            "audiomack_url",
            "boomplay_url",
            "published_at",
            "is_featured",
            "favorites_count",
            "ratings_count",
            "preview_url",
            "community_rating_average",
            "community_rating_count",
            "related_posts",
        ]
        read_only_fields = fields

    def get_preview_url(self, obj):
        """
        Return the first available provider-supplied preview URL.

        The catalog detail queryset should prefetch provider_identities.
        A fallback query keeps this serializer functional in other
        contexts where that prefetch has not been applied.
        """

        prefetched = getattr(
            obj,
            "_prefetched_objects_cache",
            {},
        ).get("provider_identities")

        if prefetched is not None:
            for identity in prefetched:
                if identity.preview_url:
                    return identity.preview_url

            return None

        return (
            obj.provider_identities
            .exclude(preview_url__isnull=True)
            .exclude(preview_url="")
            .values_list("preview_url", flat=True)
            .first()
        )

    def get_community_rating_average(self, obj):
        return get_community_rating_stats(
            obj=obj,
            target_type=CommunityPostTarget.TargetType.SONG,
            target_field="song",
        )["average"]

    def get_community_rating_count(self, obj):
        return get_community_rating_stats(
            obj=obj,
            target_type=CommunityPostTarget.TargetType.SONG,
            target_field="song",
        )["count"]

    def get_related_posts(self, obj):
        return get_related_community_posts(
            obj=obj,
            target_type=CommunityPostTarget.TargetType.SONG,
            target_field="song",
            context=self.context,
        )


# ============================================================
# ALBUM TRACK SONG
# ============================================================


class AlbumTrackSongSerializer(SongCardSerializer):
    """
    Lightweight song representation for an album's tracklist.

    Includes the provider-supplied preview URL without adding it
    to SongCardSerializer, keeping other song-card responses lean.
    """

    preview_url = serializers.SerializerMethodField()

    class Meta(SongCardSerializer.Meta):
        fields = [
            *SongCardSerializer.Meta.fields,
            "preview_url",
        ]
        read_only_fields = fields

    def get_preview_url(self, obj):
        return SongSerializer.get_preview_url(self, obj)


# ============================================================
# ALBUM TRACK
# ============================================================


class AlbumTrackSerializer(BaseModelSerializer):
    song = AlbumTrackSongSerializer(
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
# ALBUM DETAIL
# ============================================================


class AlbumSerializer(BaseModelSerializer):
    artists = ArtistCardSerializer(
        many=True,
        read_only=True,
    )

    tracks = serializers.SerializerMethodField()

    # Ratings on posts attached directly to this album.
    community_rating_average = serializers.SerializerMethodField()
    community_rating_count = serializers.SerializerMethodField()

    # Ratings on posts attached to songs in this album's tracklist.
    track_community_rating_average = serializers.SerializerMethodField()
    track_community_rating_count = serializers.SerializerMethodField()

    related_posts = serializers.SerializerMethodField()

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
            "editorial_review",
            "editorial_score",
            "spotify_url",
            "apple_music_url",
            "youtube_url",
            "audiomack_url",
            "boomplay_url",
            "published_at",
            "is_featured",
            "favorites_count",
            "ratings_count",
            "tracks",
            "community_rating_average",
            "community_rating_count",
            "track_community_rating_average",
            "track_community_rating_count",
            "related_posts",
        ]
        read_only_fields = fields

    def get_tracks(self, obj):
        """
        Preserve the model's tracklist ordering by track_number.
        The detail queryset should prefetch the tracklist and songs.
        """

        return AlbumTrackSerializer(
            obj.tracklist.all(),
            many=True,
            context=self.context,
        ).data

    def get_community_rating_average(self, obj):
        return get_community_rating_stats(
            obj=obj,
            target_type=CommunityPostTarget.TargetType.ALBUM,
            target_field="album",
        )["average"]

    def get_community_rating_count(self, obj):
        return get_community_rating_stats(
            obj=obj,
            target_type=CommunityPostTarget.TargetType.ALBUM,
            target_field="album",
        )["count"]

    def get_track_community_rating_average(self, obj):
        return get_track_community_rating_stats(obj)["average"]

    def get_track_community_rating_count(self, obj):
        return get_track_community_rating_stats(obj)["count"]

    def get_related_posts(self, obj):
        return get_related_community_posts(
            obj=obj,
            target_type=CommunityPostTarget.TargetType.ALBUM,
            target_field="album",
            context=self.context,
        )
