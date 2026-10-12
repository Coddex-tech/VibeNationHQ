from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import PurePosixPath
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from django.core.files.base import ContentFile
from django.core.files.images import get_image_dimensions
from django.db import transaction
from django.utils.dateparse import parse_date, parse_datetime
from django.utils.text import slugify

from music.models import (
    Album,
    Artist,
    MusicProviderIdentity,
    Song,
)
from music.providers.base import (
    MusicEntityType,
    MusicProviderName,
    MusicSearchResult,
)
from music.services.genre_normalization import (
    GenreNormalizer,
)


class MusicImportError(Exception):
    """
    Raised when a provider result cannot be safely imported
    into the canonical VibeNation music catalog.
    """


@dataclass(frozen=True, slots=True)
class MusicImportResult:
    """
    Result returned after importing or resolving a provider
    result into the canonical VibeNation music catalog.
    """

    entity_type: MusicEntityType
    object: Artist | Album | Song
    identity: MusicProviderIdentity
    created: bool


class MusicProviderImportService:
    """
    Converts external music-provider results into canonical
    VibeNation music records.

    This service does not perform provider searches itself.
    Searching remains the responsibility of the provider search
    layer.

    The service is responsible for:

    - resolving existing provider identities
    - resolving/creating canonical artists
    - resolving/creating canonical albums
    - resolving/creating canonical songs
    - storing provider-specific metadata
    - importing trusted provider artwork into canonical media
    - normalizing provider genres into canonical Genre records
    - preventing duplicate provider identities
    """

    ARTWORK_TIMEOUT_SECONDS = 10
    MAX_ARTWORK_BYTES = 5 * 1024 * 1024

    TRUSTED_ARTWORK_HOST_SUFFIXES = {
        MusicProviderName.ITUNES: (
            ".mzstatic.com",
        ),
    }

    @staticmethod
    def _normalized(value: str | None) -> str:
        return " ".join(
            (value or "").strip().casefold().split()
        )

    @staticmethod
    def _parse_release_date(
        value: str | None,
    ) -> date | None:
        """
        Convert provider release-date values into a Python date.

        Providers may return:

            2022
            2022-05
            2022-05-13
            2022-05-13T00:00:00Z

        Some providers may return reduced-precision dates.
        Because the canonical catalog currently uses a DateField,
        incomplete dates are normalized to the first day of the
        known period:

            2022    -> 2022-01-01
            2022-05 -> 2022-05-01

        The original provider metadata remains preserved separately
        in MusicProviderIdentity.metadata.
        """

        if not value:
            return None

        normalized_value = value.strip()

        if not normalized_value:
            return None

        parsed_date = parse_date(
            normalized_value,
        )

        if parsed_date is not None:
            return parsed_date

        parsed_datetime = parse_datetime(
            normalized_value,
        )

        if parsed_datetime is not None:
            return parsed_datetime.date()

        if len(normalized_value) == 7:
            year_part = normalized_value[:4]
            month_part = normalized_value[5:]

            if (
                year_part.isdigit()
                and normalized_value[4] == "-"
                and month_part.isdigit()
            ):
                year = int(year_part)
                month = int(month_part)

                if 1 <= month <= 12:
                    return date(
                        year,
                        month,
                        1,
                    )

        if len(normalized_value) == 4:
            if normalized_value.isdigit():
                year = int(normalized_value)

                if year > 0:
                    return date(
                        year,
                        1,
                        1,
                    )

        if len(normalized_value) >= 10:
            parsed_date = parse_date(
                normalized_value[:10],
            )

            if parsed_date is not None:
                return parsed_date

        raise MusicImportError(
            f"Invalid provider release date: "
            f"'{value}'."
        )

    @staticmethod
    def _unique_slug(
        model,
        base_value: str,
        *,
        exclude_pk: int | None = None,
    ) -> str:
        """
        Generate a unique slug for a canonical catalog record.
        """

        base_slug = slugify(
            base_value,
        ) or "music"

        queryset = model.objects.all()

        if exclude_pk is not None:
            queryset = queryset.exclude(
                pk=exclude_pk,
            )

        if not queryset.filter(
            slug=base_slug,
        ).exists():
            return base_slug

        counter = 2

        while queryset.filter(
            slug=f"{base_slug}-{counter}",
        ).exists():
            counter += 1

        return f"{base_slug}-{counter}"

    @staticmethod
    def _artwork_filename(
        url: str,
        *,
        fallback_extension: str = ".jpg",
    ) -> str:
        """
        Generate a safe filename for downloaded provider artwork.
        """

        path = PurePosixPath(
            urlparse(url).path,
        )

        suffix = path.suffix.lower()

        if suffix not in {
            ".jpg",
            ".jpeg",
            ".png",
            ".webp",
            ".gif",
        }:
            suffix = fallback_extension

        return f"provider-artwork{suffix}"

    @classmethod
    def _is_trusted_artwork_url(
        cls,
        *,
        provider: MusicProviderName,
        url: str,
    ) -> bool:
        """
        Verify that a provider artwork URL belongs to a trusted
        provider-owned artwork host.

        This is important because provider import requests contain
        URLs supplied by the client.
        """

        if not url:
            return False

        parsed = urlparse(url)

        if parsed.scheme.lower() != "https":
            return False

        hostname = (
            parsed.hostname or ""
        ).lower().rstrip(".")

        if not hostname:
            return False

        trusted_suffixes = (
            cls.TRUSTED_ARTWORK_HOST_SUFFIXES.get(
                provider,
                (),
            )
        )

        return any(
            hostname.endswith(suffix)
            for suffix in trusted_suffixes
        )

    @classmethod
    def _download_artwork(
        cls,
        *,
        provider: MusicProviderName,
        url: str | None,
    ) -> ContentFile[bytes] | None:
        """
        Download trusted provider artwork into memory.

        Only trusted provider artwork hosts are accepted.

        Downloads are deliberately size-limited so a provider import
        cannot cause an unexpectedly large file download.
        """

        if not url:
            return None

        if not cls._is_trusted_artwork_url(
            provider=provider,
            url=url,
        ):
            return None

        request = Request(
            url,
            headers={
                "User-Agent": (
                    "VibeNationHQ/1.0 "
                    "(music artwork import)"
                ),
                "Accept": (
                    "image/avif,image/webp,image/apng,"
                    "image/svg+xml,image/*,*/*;q=0.8"
                ),
            },
        )

        try:
            with urlopen(
                request,
                timeout=cls.ARTWORK_TIMEOUT_SECONDS,
            ) as response:
                content_length = response.headers.get(
                    "Content-Length",
                )

                if content_length:
                    try:
                        declared_size = int(
                            content_length,
                        )
                    except ValueError:
                        declared_size = None

                    if (
                        declared_size is not None
                        and declared_size
                        > cls.MAX_ARTWORK_BYTES
                    ):
                        return None

                chunks: list[bytes] = []
                total_size = 0

                while True:
                    chunk = response.read(64 * 1024)

                    if not chunk:
                        break

                    total_size += len(chunk)

                    if (
                        total_size
                        > cls.MAX_ARTWORK_BYTES
                    ):
                        return None

                    chunks.append(chunk)

        except (
            HTTPError,
            URLError,
            TimeoutError,
            OSError,
        ):
            return None

        content = b"".join(chunks)

        if not content:
            return None

        try:
            get_image_dimensions(
                ContentFile(content),
            )
        except Exception:
            return None

        return ContentFile(
            content,
            name=cls._artwork_filename(url),
        )

    @classmethod
    def _set_artist_artwork(
        cls,
        *,
        artist: Artist,
        result: MusicSearchResult,
    ) -> None:
        """
        Populate canonical artist artwork when the artist does not
        already have VibeNation artwork.

        This method should only be called with an actual ARTIST
        provider result.

        Existing editorial artwork is never overwritten.
        """

        if artist.profile_image:
            return

        artwork = cls._download_artwork(
            provider=result.provider,
            url=result.artwork_url,
        )

        if artwork is None:
            return

        artist.profile_image.save(
            artwork.name,
            artwork,
            save=True,
        )

    @classmethod
    def _set_album_artwork(
        cls,
        *,
        album: Album,
        result: MusicSearchResult,
    ) -> None:
        """
        Populate canonical album artwork when the album does not
        already have VibeNation artwork.

        Existing editorial artwork is never overwritten.
        """

        if album.artwork:
            return

        artwork = cls._download_artwork(
            provider=result.provider,
            url=result.artwork_url,
        )

        if artwork is None:
            return

        album.artwork.save(
            artwork.name,
            artwork,
            save=True,
        )

    @classmethod
    def _set_song_artwork(
        cls,
        *,
        song: Song,
        result: MusicSearchResult,
    ) -> None:
        """
        Populate canonical song artwork when the song does not
        already have VibeNation artwork.

        Existing editorial artwork is never overwritten.
        """

        if song.artwork:
            return

        artwork = cls._download_artwork(
            provider=result.provider,
            url=result.artwork_url,
        )

        if artwork is None:
            return

        song.artwork.save(
            artwork.name,
            artwork,
            save=True,
        )

    @staticmethod
    def _extract_genre_values(
        result: MusicSearchResult,
    ) -> list[str]:
        """
        Extract provider-supplied genre values from normalized
        provider metadata.

        Providers may expose genre information under different
        metadata keys. The canonical Genre table remains the
        source of truth.

        Unknown provider genres are handled by GenreNormalizer
        and are never automatically created.
        """

        metadata = result.metadata

        values: list[str] = []

        for key in (
            "primary_genre_name",
            "genre",
        ):
            value = metadata.get(key)

            if isinstance(value, str):
                values.append(value)

        genres = metadata.get("genres")

        if isinstance(genres, list):
            values.extend(
                value
                for value in genres
                if isinstance(value, str)
            )

        return values

    @classmethod
    def _resolve_song_genres(
        cls,
        result: MusicSearchResult,
    ):
        """
        Resolve provider genre metadata into existing canonical
        VibeNationHQ Genre records.

        This method never creates Genre records.
        """

        genre_values = cls._extract_genre_values(
            result,
        )

        if not genre_values:
            return []

        return GenreNormalizer.resolve(
            genre_values,
        )

    @classmethod
    def _attach_song_genres(
        cls,
        *,
        song: Song,
        result: MusicSearchResult,
    ) -> None:
        """
        Attach resolved canonical genres to a song.

        Existing genres are preserved because different providers
        may expose additional valid genre information for the same
        canonical song.
        """

        genres = cls._resolve_song_genres(
            result,
        )

        if not genres:
            return

        song.genres.add(
            *genres,
        )

    @classmethod
    def _find_identity(
        cls,
        result: MusicSearchResult,
    ) -> MusicProviderIdentity | None:
        return (
            MusicProviderIdentity.objects
            .select_related(
                "song",
                "album",
                "artist",
            )
            .filter(
                provider=result.provider,
                entity_type=result.entity_type,
                provider_id=result.provider_id,
            )
            .first()
        )

    @classmethod
    def _resolve_artist(
        cls,
        *,
        result: MusicSearchResult,
    ) -> Artist:
        """
        Resolve the artist associated with a provider result.

        The first lookup uses an existing provider identity.

        If no provider identity exists yet, the canonical catalog
        is matched by normalized artist name.

        Both active and inactive artists are considered during
        matching because provider-imported artists are inactive
        until they are reviewed or activated.

        An ambiguous name is rejected rather than silently
        attaching a song to the wrong artist.

        Artist artwork is intentionally not handled here.

        This method is used while importing SONG and ALBUM
        results, so result.artwork_url belongs to the song or
        album being imported, not necessarily to the artist.

        Artist artwork is only populated during an explicit
        ARTIST provider import.
        """

        artist_name = (
            result.artist_name or ""
        ).strip()

        if not artist_name:
            raise MusicImportError(
                "The provider result does not contain "
                "an artist name."
            )

        artist_provider_id = (
            result.metadata.get(
                "artist_provider_id",
            )
            or result.metadata.get(
                "artist_id",
            )
        )

        if artist_provider_id:
            identity = (
                MusicProviderIdentity.objects
                .select_related("artist")
                .filter(
                    provider=result.provider,
                    entity_type=MusicEntityType.ARTIST,
                    provider_id=str(
                        artist_provider_id,
                    ),
                )
                .first()
            )

            if identity and identity.artist:
                return identity.artist

        normalized_name = cls._normalized(
            artist_name,
        )

        candidates = [
            artist
            for artist in Artist.objects.all()
            if cls._normalized(
                artist.name,
            ) == normalized_name
        ]

        if len(candidates) == 1:
            return candidates[0]

        if len(candidates) > 1:
            raise MusicImportError(
                f"Multiple artists match "
                f"'{artist_name}'. The import cannot "
                "safely determine which artist should "
                "be used."
            )

        artist = Artist.objects.create(
            name=artist_name,
            slug=cls._unique_slug(
                Artist,
                artist_name,
            ),
            is_active=False,
        )

        if artist_provider_id:
            MusicProviderIdentity.objects.create(
                provider=result.provider,
                entity_type=MusicEntityType.ARTIST,
                provider_id=str(
                    artist_provider_id,
                ),
                artist=artist,
                artwork_url=(
                    result.artwork_url or ""
                ),
                spotify_url=(
                    result.spotify_url or ""
                ),
                apple_music_url=(
                    result.apple_music_url or ""
                ),
                youtube_url=(
                    result.youtube_url or ""
                ),
                audiomack_url=(
                    result.audiomack_url or ""
                ),
                boomplay_url=(
                    result.boomplay_url or ""
                ),
                metadata=dict(
                    result.metadata,
                ),
            )

        return artist

    @classmethod
    def _resolve_album(
        cls,
        *,
        result: MusicSearchResult,
        artist: Artist | None = None,
    ) -> Album | None:
        """
        Resolve the album associated with a provider result.

        Album imports are only attempted when the provider result
        actually contains an album title.
        """

        album_name = (
            result.album_name or ""
        ).strip()

        if not album_name:
            return None

        album_provider_id = (
            result.metadata.get(
                "album_provider_id",
            )
            or result.metadata.get(
                "album_id",
            )
        )

        if album_provider_id:
            identity = (
                MusicProviderIdentity.objects
                .select_related("album")
                .filter(
                    provider=result.provider,
                    entity_type=MusicEntityType.ALBUM,
                    provider_id=str(
                        album_provider_id,
                    ),
                )
                .first()
            )

            if identity and identity.album:
                if (
                    artist is not None
                    and not identity.album.artists.filter(
                        pk=artist.pk,
                    ).exists()
                ):
                    identity.album.artists.add(
                        artist,
                    )

                cls._set_album_artwork(
                    album=identity.album,
                    result=result,
                )

                return identity.album

        normalized_name = cls._normalized(
            album_name,
        )

        candidates = [
            album
            for album in Album.objects.all()
            if cls._normalized(
                album.title,
            ) == normalized_name
        ]

        if artist is not None:
            artist_candidates = [
                album
                for album in candidates
                if album.artists.filter(
                    pk=artist.pk,
                ).exists()
            ]

            if artist_candidates:
                candidates = artist_candidates

        if len(candidates) == 1:
            album = candidates[0]

            if artist is not None:
                album.artists.add(
                    artist,
                )

            cls._set_album_artwork(
                album=album,
                result=result,
            )

            return album

        if len(candidates) > 1:
            raise MusicImportError(
                f"Multiple albums match "
                f"'{album_name}'. The import cannot "
                "safely determine which album should "
                "be used."
            )

        album = Album.objects.create(
            title=album_name,
            slug=cls._unique_slug(
                Album,
                album_name,
            ),
            release_date=cls._parse_release_date(
                result.release_date,
            ),
        )

        if artist is not None:
            album.artists.add(
                artist,
            )

        cls._set_album_artwork(
            album=album,
            result=result,
        )

        if album_provider_id:
            MusicProviderIdentity.objects.create(
                provider=result.provider,
                entity_type=MusicEntityType.ALBUM,
                provider_id=str(
                    album_provider_id,
                ),
                album=album,
                artwork_url=(
                    result.artwork_url or ""
                ),
                spotify_url=(
                    result.spotify_url or ""
                ),
                apple_music_url=(
                    result.apple_music_url or ""
                ),
                youtube_url=(
                    result.youtube_url or ""
                ),
                audiomack_url=(
                    result.audiomack_url or ""
                ),
                boomplay_url=(
                    result.boomplay_url or ""
                ),
                metadata=dict(
                    result.metadata,
                ),
            )

        return album

    @classmethod
    def _import_artist(
        cls,
        result: MusicSearchResult,
    ) -> MusicImportResult:
        existing_identity = cls._find_identity(
            result,
        )

        if existing_identity:
            if not existing_identity.artist:
                raise MusicImportError(
                    "The provider identity is not linked "
                    "to an artist."
                )

            cls._set_artist_artwork(
                artist=existing_identity.artist,
                result=result,
            )

            return MusicImportResult(
                entity_type=result.entity_type,
                object=existing_identity.artist,
                identity=existing_identity,
                created=False,
            )

        artist_name = result.title.strip()

        if not artist_name:
            raise MusicImportError(
                "The provider result does not contain "
                "an artist name."
            )

        normalized_name = cls._normalized(
            artist_name,
        )

        candidates = [
            artist
            for artist in Artist.objects.all()
            if cls._normalized(
                artist.name,
            ) == normalized_name
        ]

        if len(candidates) > 1:
            raise MusicImportError(
                f"Multiple artists match "
                f"'{artist_name}'. The import cannot "
                "safely determine which artist should "
                "be used."
            )

        if candidates:
            artist = candidates[0]
            created = False
        else:
            artist = Artist.objects.create(
                name=artist_name,
                slug=cls._unique_slug(
                    Artist,
                    artist_name,
                ),
                is_active=False,
            )
            created = True

        cls._set_artist_artwork(
            artist=artist,
            result=result,
        )

        identity = MusicProviderIdentity.objects.create(
            provider=result.provider,
            entity_type=result.entity_type,
            provider_id=result.provider_id,
            artist=artist,
            artwork_url=(
                result.artwork_url or ""
            ),
            spotify_url=(
                result.spotify_url or ""
            ),
            apple_music_url=(
                result.apple_music_url or ""
            ),
            youtube_url=(
                result.youtube_url or ""
            ),
            audiomack_url=(
                result.audiomack_url or ""
            ),
            boomplay_url=(
                result.boomplay_url or ""
            ),
            metadata=dict(
                result.metadata,
            ),
        )

        return MusicImportResult(
            entity_type=result.entity_type,
            object=artist,
            identity=identity,
            created=created,
        )

    @classmethod
    def _import_album(
        cls,
        result: MusicSearchResult,
    ) -> MusicImportResult:
        existing_identity = cls._find_identity(
            result,
        )

        if existing_identity:
            if not existing_identity.album:
                raise MusicImportError(
                    "The provider identity is not linked "
                    "to an album."
                )

            cls._set_album_artwork(
                album=existing_identity.album,
                result=result,
            )

            return MusicImportResult(
                entity_type=result.entity_type,
                object=existing_identity.album,
                identity=existing_identity,
                created=False,
            )

        artist = None

        if result.artist_name:
            artist = cls._resolve_artist(
                result=result,
            )

        album_name = result.title.strip()

        if not album_name:
            raise MusicImportError(
                "The provider result does not contain "
                "an album title."
            )

        normalized_name = cls._normalized(
            album_name,
        )

        candidates = [
            album
            for album in Album.objects.all()
            if cls._normalized(
                album.title,
            ) == normalized_name
        ]

        if artist is not None:
            artist_candidates = [
                album
                for album in candidates
                if album.artists.filter(
                    pk=artist.pk,
                ).exists()
            ]

            if artist_candidates:
                candidates = artist_candidates

        if len(candidates) > 1:
            raise MusicImportError(
                f"Multiple albums match "
                f"'{album_name}'. The import cannot "
                "safely determine which album should "
                "be used."
            )

        if candidates:
            album = candidates[0]
            created = False
        else:
            album = Album.objects.create(
                title=album_name,
                slug=cls._unique_slug(
                    Album,
                    album_name,
                ),
                release_date=cls._parse_release_date(
                    result.release_date,
                ),
            )
            created = True

        if artist is not None:
            album.artists.add(
                artist,
            )

        cls._set_album_artwork(
            album=album,
            result=result,
        )

        identity = MusicProviderIdentity.objects.create(
            provider=result.provider,
            entity_type=result.entity_type,
            provider_id=result.provider_id,
            album=album,
            artwork_url=(
                result.artwork_url or ""
            ),
            spotify_url=(
                result.spotify_url or ""
            ),
            apple_music_url=(
                result.apple_music_url or ""
            ),
            youtube_url=(
                result.youtube_url or ""
            ),
            audiomack_url=(
                result.audiomack_url or ""
            ),
            boomplay_url=(
                result.boomplay_url or ""
            ),
            metadata=dict(
                result.metadata,
            ),
        )

        return MusicImportResult(
            entity_type=result.entity_type,
            object=album,
            identity=identity,
            created=created,
        )

    @classmethod
    def _import_song(
        cls,
        result: MusicSearchResult,
    ) -> MusicImportResult:
        existing_identity = cls._find_identity(
            result,
        )

        if existing_identity:
            if not existing_identity.song:
                raise MusicImportError(
                    "The provider identity is not linked "
                    "to a song."
                )

            cls._set_song_artwork(
                song=existing_identity.song,
                result=result,
            )

            cls._attach_song_genres(
                song=existing_identity.song,
                result=result,
            )

            return MusicImportResult(
                entity_type=result.entity_type,
                object=existing_identity.song,
                identity=existing_identity,
                created=False,
            )

        artist = cls._resolve_artist(
            result=result,
        )

        album = cls._resolve_album(
            result=result,
            artist=artist,
        )

        song_title = result.title.strip()

        if not song_title:
            raise MusicImportError(
                "The provider result does not contain "
                "a song title."
            )

        slug_base = (
            f"{song_title} {artist.name}"
        )

        normalized_title = cls._normalized(
            song_title,
        )

        candidates = [
            song
            for song in Song.objects.prefetch_related(
                "artists",
            )
            if cls._normalized(
                song.title,
            ) == normalized_title
            and song.artists.filter(
                pk=artist.pk,
            ).exists()
        ]

        if len(candidates) > 1:
            raise MusicImportError(
                f"Multiple songs match "
                f"'{song_title}' by '{artist.name}'. "
                "The import cannot safely determine "
                "which song should be used."
            )

        if candidates:
            song = candidates[0]
            created = False
        else:
            song = Song.objects.create(
                title=song_title,
                slug=cls._unique_slug(
                    Song,
                    slug_base,
                ),
                album=album,
                release_date=cls._parse_release_date(
                    result.release_date,
                ),
                duration_seconds=(
                    result.duration_seconds
                ),
            )
            created = True

        song.artists.add(
            artist,
        )

        if album is not None:
            if song.album_id != album.id:
                song.album = album
                song.save(
                    update_fields=[
                        "album",
                        "updated_at",
                    ],
                )

        cls._set_song_artwork(
            song=song,
            result=result,
        )

        cls._attach_song_genres(
            song=song,
            result=result,
        )

        identity = MusicProviderIdentity.objects.create(
            provider=result.provider,
            entity_type=result.entity_type,
            provider_id=result.provider_id,
            song=song,
            artwork_url=(
                result.artwork_url or ""
            ),
            preview_url=(
                result.preview_url or ""
            ),
            spotify_url=(
                result.spotify_url or ""
            ),
            apple_music_url=(
                result.apple_music_url or ""
            ),
            youtube_url=(
                result.youtube_url or ""
            ),
            audiomack_url=(
                result.audiomack_url or ""
            ),
            boomplay_url=(
                result.boomplay_url or ""
            ),
            metadata=dict(
                result.metadata,
            ),
        )

        return MusicImportResult(
            entity_type=result.entity_type,
            object=song,
            identity=identity,
            created=created,
        )

    @classmethod
    @transaction.atomic
    def import_result(
        cls,
        result: MusicSearchResult,
    ) -> MusicImportResult:
        """
        Import or resolve one provider search result.

        The complete operation runs inside a database
        transaction so a partially-created catalog record
        cannot be left behind if something fails.
        """

        if not result.provider_id.strip():
            raise MusicImportError(
                "Provider result is missing its provider ID."
            )

        if not result.title.strip():
            raise MusicImportError(
                "Provider result is missing its title."
            )

        if result.entity_type == MusicEntityType.ARTIST:
            return cls._import_artist(
                result,
            )

        if result.entity_type == MusicEntityType.ALBUM:
            return cls._import_album(
                result,
            )

        if result.entity_type == MusicEntityType.SONG:
            return cls._import_song(
                result,
            )

        raise MusicImportError(
            f"Unsupported music entity type: "
            f"{result.entity_type}"
        )