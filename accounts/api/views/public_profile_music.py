from rest_framework.response import Response
from rest_framework import generics
from rest_framework.permissions import AllowAny

from django.contrib.auth import get_user_model
from django.db.models import (
    CharField,
    Count,
    F,
    Max,
    Value,
)
from django.shortcuts import get_object_or_404

from accounts.authentications import (
    VibeNationSessionAuthentication,
)
from accounts.serializers.public_profile_music import (
    PublicProfileMusicItemSerializer,
)
from music.api.pagination import MusicPagination
from music.models import (
    Album,
    Artist,
    CommunityPost,
    CommunityPostTarget,
    Song,
)


User = get_user_model()


class PublicProfileMusicView(generics.ListAPIView):
    """
    List the unique canonical music entities a public user
    has posted about.

    Each entity appears once, ordered by the user's most
    recent published post about that entity.

    The database performs aggregation and pagination before
    catalog entities are hydrated for the requested page.
    """

    authentication_classes = [
        VibeNationSessionAuthentication,
    ]

    permission_classes = [
        AllowAny,
    ]

    serializer_class = PublicProfileMusicItemSerializer
    pagination_class = MusicPagination

    lookup_url_kwarg = "username"

    # ========================================================
    # PROFILE
    # ========================================================

    def get_profile(self):
        """
        Retrieve the publicly visible profile whose Music
        timeline is being requested.
        """

        if not hasattr(self, "_profile"):
            username = self.kwargs.get(
                self.lookup_url_kwarg,
            )

            self._profile = get_object_or_404(
                User.objects.filter(
                    is_active=True,
                    is_staff=False,
                    is_superuser=False,
                    onboarding_completed=True,
                ),
                username__iexact=username,
            )

        return self._profile

    # ========================================================
    # AGGREGATION
    # ========================================================

    def get_queryset(self):
        """
        Aggregate published posts into unique canonical
        song, album, and artist entities.

        Each aggregation returns the same four columns:

            target_type
            entity_id
            post_count
            latest_post_at

        UNION ALL combines the three entity types without
        loading all results into Python.
        """

        profile = self.get_profile()

        published_posts = (
            CommunityPost.objects
            .filter(
                user=profile,
                status=CommunityPost.Status.PUBLISHED,
            )
            .order_by()
        )

        # ----------------------------------------------------
        # Songs
        # ----------------------------------------------------

        song_queryset = (
            published_posts
            .filter(
                target__target_type=(
                    CommunityPostTarget.TargetType.SONG
                ),
                target__song__isnull=False,
            )
            .values(
                "target__song_id",
            )
            .annotate(
                post_count=Count("pk"),
                latest_post_at=Max("created_at"),
            )
            .annotate(
                target_type=Value(
                    "song",
                    output_field=CharField(),
                ),
                entity_id=F("target__song_id"),
            )
            .values(
                "target_type",
                "entity_id",
                "post_count",
                "latest_post_at",
            )
        )

        # ----------------------------------------------------
        # Albums
        # ----------------------------------------------------

        album_queryset = (
            published_posts
            .filter(
                target__target_type=(
                    CommunityPostTarget.TargetType.ALBUM
                ),
                target__album__isnull=False,
            )
            .values(
                "target__album_id",
            )
            .annotate(
                post_count=Count("pk"),
                latest_post_at=Max("created_at"),
            )
            .annotate(
                target_type=Value(
                    "album",
                    output_field=CharField(),
                ),
                entity_id=F("target__album_id"),
            )
            .values(
                "target_type",
                "entity_id",
                "post_count",
                "latest_post_at",
            )
        )

        # ----------------------------------------------------
        # Artists
        # ----------------------------------------------------

        artist_queryset = (
            published_posts
            .filter(
                target__target_type=(
                    CommunityPostTarget.TargetType.ARTIST
                ),
                target__artist__isnull=False,
            )
            .values(
                "target__artist_id",
            )
            .annotate(
                post_count=Count("pk"),
                latest_post_at=Max("created_at"),
            )
            .annotate(
                target_type=Value(
                    "artist",
                    output_field=CharField(),
                ),
                entity_id=F("target__artist_id"),
            )
            .values(
                "target_type",
                "entity_id",
                "post_count",
                "latest_post_at",
            )
        )

        # ----------------------------------------------------
        # Combine and order
        # ----------------------------------------------------

        return (
            song_queryset
            .union(
                album_queryset,
                artist_queryset,
                all=True,
            )
            .order_by(
                "-latest_post_at",
                "target_type",
                "entity_id",
            )
        )

    # ========================================================
    # ENTITY HYDRATION
    # ========================================================

    def hydrate_entities(self, aggregated_items):
        """
        Load only the catalog entities represented on the
        requested page.

        Songs and albums have their artist relationships
        prefetched for their existing card serializers.
        """

        items = list(aggregated_items)

        if not items:
            return items

        song_ids = [
            item["entity_id"]
            for item in items
            if item["target_type"] == "song"
        ]

        album_ids = [
            item["entity_id"]
            for item in items
            if item["target_type"] == "album"
        ]

        artist_ids = [
            item["entity_id"]
            for item in items
            if item["target_type"] == "artist"
        ]

        # ----------------------------------------------------
        # Hydrate songs
        # ----------------------------------------------------

        songs = {
            song.pk: song
            for song in (
                Song.objects
                .filter(pk__in=song_ids)
                .prefetch_related(
                    "artists",
                    "featured_artists",
                )
            )
        }

        # ----------------------------------------------------
        # Hydrate albums
        # ----------------------------------------------------

        albums = {
            album.pk: album
            for album in (
                Album.objects
                .filter(pk__in=album_ids)
                .prefetch_related(
                    "artists",
                )
            )
        }

        # ----------------------------------------------------
        # Hydrate artists
        # ----------------------------------------------------

        artists = {
            artist.pk: artist
            for artist in Artist.objects.filter(
                pk__in=artist_ids,
            )
        }

        # ----------------------------------------------------
        # Attach hydrated entities
        # ----------------------------------------------------

        entity_maps = {
            "song": songs,
            "album": albums,
            "artist": artists,
        }

        hydrated_items = []

        for item in items:
            entity = entity_maps[
                item["target_type"]
            ].get(
                item["entity_id"],
            )

            # A catalog entity may have been deleted between
            # aggregation and hydration. Skip missing records.
            if entity is None:
                continue

            hydrated_items.append({
                **item,
                "entity": entity,
            })

        return hydrated_items

    # ========================================================
    # RESPONSE
    # ========================================================

    def list(self, request, *args, **kwargs):
        """
        Paginate aggregation results first, then hydrate
        and serialize only the requested page.
        """

        queryset = self.get_queryset()

        page = self.paginate_queryset(
            queryset,
        )

        if page is not None:
            items = self.hydrate_entities(
                page,
            )

            serializer = self.get_serializer(
                items,
                many=True,
            )

            return self.get_paginated_response(
                serializer.data,
            )

        items = self.hydrate_entities(
            queryset,
        )

        serializer = self.get_serializer(
            items,
            many=True,
        )

        return Response(
            serializer.data,
        )
