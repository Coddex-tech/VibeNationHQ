from django.db.models import Case, IntegerField, Q, Value, When

from music.models import (
    Album,
    Artist,
    Genre,
    Song,
)


class MusicSearchService:
    """
    Search the public VibeNation music catalog.

    Searches:
    - Songs
    - Artists
    - Albums
    - Genres

    Only published/active catalog records are returned.
    """

    RESULT_LIMIT = 10

    @classmethod
    def search_songs(cls, query):
        return (
            Song.objects
            .filter(
                status=Song.Status.PUBLISHED,
            )
            .filter(
                Q(title__icontains=query)
                | Q(artists__name__icontains=query)
                | Q(featured_artists__name__icontains=query)
            )
            .select_related("album")
            .prefetch_related(
                "artists",
                "featured_artists",
                "genres",
            )
            .annotate(
                search_priority=Case(
                    When(
                        title__iexact=query,
                        then=Value(0),
                    ),
                    When(
                        title__istartswith=query,
                        then=Value(1),
                    ),
                    default=Value(2),
                    output_field=IntegerField(),
                )
            )
            .distinct()
            .order_by(
                "search_priority",
                "-published_at",
            )[:cls.RESULT_LIMIT]
        )

    @classmethod
    def search_artists(cls, query):
        return (
            Artist.objects
            .filter(
                is_active=True,
            )
            .filter(
                name__icontains=query,
            )
            .annotate(
                search_priority=Case(
                    When(
                        name__iexact=query,
                        then=Value(0),
                    ),
                    When(
                        name__istartswith=query,
                        then=Value(1),
                    ),
                    default=Value(2),
                    output_field=IntegerField(),
                )
            )
            .order_by(
                "search_priority",
                "name",
            )[:cls.RESULT_LIMIT]
        )

    @classmethod
    def search_albums(cls, query):
        return (
            Album.objects
            .filter(
                status=Album.Status.PUBLISHED,
            )
            .filter(
                Q(title__icontains=query)
                | Q(artists__name__icontains=query)
            )
            .prefetch_related(
                "artists",
            )
            .annotate(
                search_priority=Case(
                    When(
                        title__iexact=query,
                        then=Value(0),
                    ),
                    When(
                        title__istartswith=query,
                        then=Value(1),
                    ),
                    default=Value(2),
                    output_field=IntegerField(),
                )
            )
            .distinct()
            .order_by(
                "search_priority",
                "-release_date",
                "-published_at",
            )[:cls.RESULT_LIMIT]
        )

    @classmethod
    def search_genres(cls, query):
        return (
            Genre.objects
            .filter(
                is_active=True,
                name__icontains=query,
            )
            .annotate(
                search_priority=Case(
                    When(
                        name__iexact=query,
                        then=Value(0),
                    ),
                    When(
                        name__istartswith=query,
                        then=Value(1),
                    ),
                    default=Value(2),
                    output_field=IntegerField(),
                )
            )
            .order_by(
                "search_priority",
                "name",
            )[:cls.RESULT_LIMIT]
        )

    @classmethod
    def search(cls, query):
        """
        Execute a complete catalog search.
        """

        query = query.strip()

        return {
            "songs": cls.search_songs(query),
            "artists": cls.search_artists(query),
            "albums": cls.search_albums(query),
            "genres": cls.search_genres(query),
        }