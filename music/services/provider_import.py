
from __future__ import annotations

import ipaddress
from dataclasses import dataclass
from datetime import date
from pathlib import PurePosixPath
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import (
    HTTPRedirectHandler,
    Request,
    build_opener,
)

from django.core.files.base import ContentFile
from django.core.files.images import get_image_dimensions
from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime
from django.utils.text import slugify

from music.models import (
    Album,
    AlbumTrack,
    Artist,
    MusicProviderIdentity,
    Song,
)
from music.providers.base import (
    MusicEntityType,
    MusicProviderError,
    MusicProviderName,
    MusicSearchResult,
)
from music.providers.registry import MusicProviderRegistry
from music.services.genre_normalization import GenreNormalizer


class MusicImportError(Exception):
    """Raised when a provider result cannot be safely imported."""


@dataclass(frozen=True, slots=True)
class MusicImportResult:
    """Result returned after importing or resolving a provider result."""

    entity_type: MusicEntityType
    object: Artist | Album | Song
    identity: MusicProviderIdentity
    created: bool


class _TrustedArtworkRedirectHandler(HTTPRedirectHandler):
    """
    Reject redirects to hosts outside the trusted artwork domain.

    This prevents a trusted artwork URL from redirecting the
    downloader to an unrelated host.
    """

    def __init__(self, provider: MusicProviderName):
        super().__init__()
        self.provider = provider

    def redirect_request(
        self,
        req,
        fp,
        code,
        msg,
        headers,
        newurl,
    ):
        if not MusicProviderImportService._is_trusted_artwork_url(
            provider=self.provider,
            url=newurl,
        ):
            return None

        return super().redirect_request(
            req,
            fp,
            code,
            msg,
            headers,
            newurl,
        )


class MusicProviderImportService:
    """Import external provider results into the canonical music catalog."""

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
    def _parse_release_date(value: str | None) -> date | None:
        """
        Parse full or reduced-precision provider dates.

        A year becomes January 1; a year-month becomes the first
        day of that month. The original provider metadata remains
        stored on MusicProviderIdentity.
        """
        if not value:
            return None

        normalized_value = value.strip()

        if not normalized_value:
            return None

        parsed_date = parse_date(normalized_value)

        if parsed_date is not None:
            return parsed_date

        parsed_datetime = parse_datetime(normalized_value)

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
                    return date(year, month, 1)

        if len(normalized_value) == 4 and normalized_value.isdigit():
            year = int(normalized_value)

            if year > 0:
                return date(year, 1, 1)

        if len(normalized_value) >= 10:
            parsed_date = parse_date(normalized_value[:10])

            if parsed_date is not None:
                return parsed_date

        raise MusicImportError(
            f"Invalid provider release date: '{value}'."
        )

    @staticmethod
    def _unique_slug(
        model,
        base_value: str,
        *,
        exclude_pk: int | None = None,
    ) -> str:
        """Generate a currently unused slug for a catalog record."""
        base_slug = slugify(base_value) or "music"

        queryset = model.objects.all()

        if exclude_pk is not None:
            queryset = queryset.exclude(pk=exclude_pk)

        if not queryset.filter(slug=base_slug).exists():
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
        """Generate a safe filename for provider artwork."""
        path = PurePosixPath(urlparse(url).path)
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
        """Allow only HTTPS artwork URLs from explicitly trusted hosts."""
        if not url:
            return False

        try:
            parsed = urlparse(url)
            hostname = (parsed.hostname or "").lower().rstrip(".")

            # Reject credentials, unexpected ports, non-HTTPS URLs,
            # and malformed hostnames.
            if (
                parsed.scheme.lower() != "https"
                or not hostname
                or parsed.username is not None
                or parsed.password is not None
                or parsed.port not in (None, 443)
            ):
                return False

            # Reject IP literals rather than allowing an address to
            # masquerade as a provider artwork host.
            try:
                ipaddress.ip_address(hostname)
                return False
            except ValueError:
                pass

        except ValueError:
            return False

        trusted_suffixes = cls.TRUSTED_ARTWORK_HOST_SUFFIXES.get(
            provider,
            (),
        )

        return any(
            hostname.endswith(suffix)
            and hostname != suffix.lstrip(".")
            for suffix in trusted_suffixes
        )

    @classmethod
    def _download_artwork(
        cls,
        *,
        provider: MusicProviderName,
        url: str | None,
    ) -> ContentFile[bytes] | None:
        """Download size-limited artwork from trusted provider hosts."""
        if not url or not cls._is_trusted_artwork_url(
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
                "Accept": "image/jpeg,image/png,image/webp,image/*",
            },
        )

        opener = build_opener(
            _TrustedArtworkRedirectHandler(provider),
        )

        try:
            with opener.open(
                request,
                timeout=cls.ARTWORK_TIMEOUT_SECONDS,
            ) as response:
                final_url = response.geturl()

                if not cls._is_trusted_artwork_url(
                    provider=provider,
                    url=final_url,
                ):
                    return None

                content_length = response.headers.get("Content-Length")

                if content_length:
                    try:
                        declared_size = int(content_length)
                    except ValueError:
                        declared_size = None

                    if (
                        declared_size is not None
                        and (
                            declared_size < 0
                            or declared_size > cls.MAX_ARTWORK_BYTES
                        )
                    ):
                        return None

                chunks: list[bytes] = []
                total_size = 0

                while True:
                    chunk = response.read(64 * 1024)

                    if not chunk:
                        break

                    total_size += len(chunk)

                    if total_size > cls.MAX_ARTWORK_BYTES:
                        return None

                    chunks.append(chunk)

        except (
            HTTPError,
            URLError,
            TimeoutError,
            OSError,
            ValueError,
        ):
            return None

        content = b"".join(chunks)

        if not content:
            return None

        image_file = ContentFile(content)

        try:
            dimensions = get_image_dimensions(image_file)
        except Exception:
            return None

        if not dimensions or not all(dimensions):
            return None

        image_file.seek(0)

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
        """Populate missing artist artwork without replacing editorial artwork."""
        if artist.profile_image:
            return

        artwork = cls._download_artwork(
            provider=result.provider,
            url=result.artwork_url,
        )

        if artwork is not None:
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
        """Populate missing album artwork without replacing existing artwork."""
        if album.artwork:
            return

        artwork = cls._download_artwork(
            provider=result.provider,
            url=result.artwork_url,
        )

        if artwork is not None:
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
        """Populate missing song artwork without replacing existing artwork."""
        if song.artwork:
            return

        artwork = cls._download_artwork(
            provider=result.provider,
            url=result.artwork_url,
        )

        if artwork is not None:
            song.artwork.save(
                artwork.name,
                artwork,
                save=True,
            )

    @staticmethod
    def _extract_genre_values(
        result: MusicSearchResult,
    ) -> list[str]:
        """Extract supported genre values from provider metadata."""
        metadata = result.metadata
        values: list[str] = []

        for key in ("primary_genre_name", "genre"):
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
        """Resolve provider genres without automatically creating genres."""
        genre_values = cls._extract_genre_values(result)

        if not genre_values:
            return []

        return GenreNormalizer.resolve(genre_values)

    @classmethod
    def _attach_song_genres(
        cls,
        *,
        song: Song,
        result: MusicSearchResult,
    ) -> None:
        """Attach recognized genres while preserving existing genres."""
        genres = cls._resolve_song_genres(result)

        if genres:
            song.genres.add(*genres)

    @classmethod
    def _find_identity(
        cls,
        result: MusicSearchResult,
    ) -> MusicProviderIdentity | None:
        return (
            MusicProviderIdentity.objects
            .select_related("song", "album", "artist")
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
        """Resolve an artist by provider identity or exact normalized name."""
        artist_name = (result.artist_name or "").strip()

        if not artist_name:
            raise MusicImportError(
                "The provider result does not contain an artist name."
            )

        artist_provider_id = (
            result.metadata.get("artist_provider_id")
            or result.metadata.get("artist_id")
        )

        if artist_provider_id:
            identity = (
                MusicProviderIdentity.objects
                .select_related("artist")
                .filter(
                    provider=result.provider,
                    entity_type=MusicEntityType.ARTIST,
                    provider_id=str(artist_provider_id),
                )
                .first()
            )

            if identity and identity.artist:
                return identity.artist

        normalized_name = cls._normalized(artist_name)

        candidates = [
            artist
            for artist in Artist.objects.all()
            if cls._normalized(artist.name) == normalized_name
        ]

        if len(candidates) == 1:
            return candidates[0]

        if len(candidates) > 1:
            raise MusicImportError(
                f"Multiple artists match '{artist_name}'. "
                "The import cannot safely determine which artist to use."
            )

        artist = Artist.objects.create(
            name=artist_name,
            slug=cls._unique_slug(Artist, artist_name),
            is_active=False,
        )

        if artist_provider_id:
            MusicProviderIdentity.objects.create(
                provider=result.provider,
                entity_type=MusicEntityType.ARTIST,
                provider_id=str(artist_provider_id),
                artist=artist,
                artwork_url=result.artwork_url or "",
                spotify_url=result.spotify_url or "",
                apple_music_url=result.apple_music_url or "",
                youtube_url=result.youtube_url or "",
                audiomack_url=result.audiomack_url or "",
                boomplay_url=result.boomplay_url or "",
                metadata=dict(result.metadata),
            )

        return artist

    @classmethod
    def _resolve_album(
        cls,
        *,
        result: MusicSearchResult,
        artist: Artist | None = None,
    ) -> Album | None:
        """Resolve an album by provider identity or title and artist."""
        album_name = (result.album_name or "").strip()

        if not album_name:
            return None

        album_provider_id = (
            result.metadata.get("album_provider_id")
            or result.metadata.get("album_id")
            or result.metadata.get("collection_id")
        )

        if album_provider_id:
            identity = (
                MusicProviderIdentity.objects
                .select_related("album")
                .filter(
                    provider=result.provider,
                    entity_type=MusicEntityType.ALBUM,
                    provider_id=str(album_provider_id),
                )
                .first()
            )

            if identity and identity.album:
                album = identity.album

                if (
                    artist is not None
                    and not album.artists.filter(pk=artist.pk).exists()
                ):
                    album.artists.add(artist)

                cls._set_album_artwork(
                    album=album,
                    result=result,
                )

                return album

        normalized_name = cls._normalized(album_name)

        candidates = [
            album
            for album in Album.objects.all()
            if cls._normalized(album.title) == normalized_name
        ]

        if artist is not None:
            candidates = [
                album
                for album in candidates
                if album.artists.filter(pk=artist.pk).exists()
            ]

        if len(candidates) > 1:
            raise MusicImportError(
                f"Multiple albums match '{album_name}'. "
                "The import cannot safely determine which album to use."
            )

        if candidates:
            album = candidates[0]
            cls._set_album_artwork(album=album, result=result)
            return album

        album = Album.objects.create(
            title=album_name,
            slug=cls._unique_slug(Album, album_name),
            release_date=cls._parse_release_date(result.release_date),
        )

        if artist is not None:
            album.artists.add(artist)

        cls._set_album_artwork(album=album, result=result)

        if album_provider_id:
            MusicProviderIdentity.objects.create(
                provider=result.provider,
                entity_type=MusicEntityType.ALBUM,
                provider_id=str(album_provider_id),
                album=album,
                artwork_url=result.artwork_url or "",
                spotify_url=result.spotify_url or "",
                apple_music_url=result.apple_music_url or "",
                youtube_url=result.youtube_url or "",
                audiomack_url=result.audiomack_url or "",
                boomplay_url=result.boomplay_url or "",
                metadata=dict(result.metadata),
            )

        return album

    @classmethod
    def _import_artist(
        cls,
        result: MusicSearchResult,
    ) -> MusicImportResult:
        existing_identity = cls._find_identity(result)

        if existing_identity:
            if not existing_identity.artist:
                raise MusicImportError(
                    "The provider identity is not linked to an artist."
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
                "The provider result does not contain an artist name."
            )

        normalized_name = cls._normalized(artist_name)

        candidates = [
            artist
            for artist in Artist.objects.all()
            if cls._normalized(artist.name) == normalized_name
        ]

        if len(candidates) > 1:
            raise MusicImportError(
                f"Multiple artists match '{artist_name}'. "
                "The import cannot safely determine which artist to use."
            )

        if candidates:
            artist = candidates[0]
            created = False
        else:
            artist = Artist.objects.create(
                name=artist_name,
                slug=cls._unique_slug(Artist, artist_name),
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
            artwork_url=result.artwork_url or "",
            spotify_url=result.spotify_url or "",
            apple_music_url=result.apple_music_url or "",
            youtube_url=result.youtube_url or "",
            audiomack_url=result.audiomack_url or "",
            boomplay_url=result.boomplay_url or "",
            metadata=dict(result.metadata),
        )

        return MusicImportResult(
            entity_type=result.entity_type,
            object=artist,
            identity=identity,
            created=created,
        )

    @classmethod
    def _sync_album_tracklist(
        cls,
        *,
        album: Album,
        result: MusicSearchResult,
    ) -> bool:
        """
        Synchronize an album tracklist atomically.

        If track resolution or validation fails, imports performed
        during this synchronization attempt are rolled back and the
        existing tracklist is preserved.
        """
        registry = MusicProviderRegistry()

        try:
            provider = registry.get(result.provider)
        except (ValueError, MusicProviderError):
            return False

        get_album_tracks = getattr(provider, "get_album_tracks", None)

        if not callable(get_album_tracks):
            return False

        try:
            provider_tracks = get_album_tracks(
                album_provider_id=result.provider_id,
                country=result.country or "NG",
            )
        except MusicProviderError:
            return False

        if not provider_tracks:
            return False

        expected_track_count = result.metadata.get("track_count")

        if expected_track_count is not None:
            try:
                expected_track_count = int(expected_track_count)
            except (TypeError, ValueError):
                expected_track_count = None

        if (
            expected_track_count is not None
            and expected_track_count > 0
            and len(provider_tracks) != expected_track_count
        ):
            return False

        provider_track_keys = []

        for track_result in provider_tracks:
            if track_result.entity_type != MusicEntityType.SONG:
                return False

            provider_id = (track_result.provider_id or "").strip()

            if not provider_id:
                return False

            provider_track_keys.append(
                (
                    track_result.provider,
                    track_result.entity_type,
                    provider_id,
                )
            )

        if len(provider_track_keys) != len(set(provider_track_keys)):
            return False

        try:
            with transaction.atomic():
                resolved_songs: list[Song] = []

                for track_result in provider_tracks:
                    imported_track = cls._import_song(track_result)

                    if not isinstance(imported_track.object, Song):
                        raise MusicImportError(
                            "An album track could not be resolved to a song."
                        )

                    resolved_songs.append(imported_track.object)

                song_ids = [song.pk for song in resolved_songs]

                if len(song_ids) != len(set(song_ids)):
                    raise MusicImportError(
                        "The provider tracklist contains duplicate canonical songs."
                    )

                AlbumTrack.objects.filter(album=album).delete()

                AlbumTrack.objects.bulk_create(
                    [
                        AlbumTrack(
                            album=album,
                            song=song,
                            track_number=position,
                        )
                        for position, song in enumerate(
                            resolved_songs,
                            start=1,
                        )
                    ]
                )

        except MusicImportError:
            return False

        return True

    @staticmethod
    def _publish_imported_album(album: Album) -> None:
        """Publish imported albums unless they are archived."""
        if album.status == Album.Status.ARCHIVED:
            return

        update_fields = []

        if album.status != Album.Status.PUBLISHED:
            album.status = Album.Status.PUBLISHED
            update_fields.append("status")

        if album.published_at is None:
            album.published_at = timezone.now()
            update_fields.append("published_at")

        if update_fields:
            update_fields.append("updated_at")
            album.save(update_fields=update_fields)

    @classmethod
    def _import_album(
        cls,
        result: MusicSearchResult,
    ) -> MusicImportResult:
        existing_identity = cls._find_identity(result)

        if existing_identity:
            if not existing_identity.album:
                raise MusicImportError(
                    "The provider identity is not linked to an album."
                )

            album = existing_identity.album

            cls._set_album_artwork(album=album, result=result)
            cls._publish_imported_album(album)
            cls._sync_album_tracklist(album=album, result=result)

            return MusicImportResult(
                entity_type=result.entity_type,
                object=album,
                identity=existing_identity,
                created=False,
            )

        artist = None

        if result.artist_name:
            artist = cls._resolve_artist(result=result)

        album_name = result.title.strip()

        if not album_name:
            raise MusicImportError(
                "The provider result does not contain an album title."
            )

        normalized_name = cls._normalized(album_name)

        candidates = [
            album
            for album in Album.objects.all()
            if cls._normalized(album.title) == normalized_name
        ]

        if artist is not None:
            candidates = [
                album
                for album in candidates
                if album.artists.filter(pk=artist.pk).exists()
            ]

        if len(candidates) > 1:
            raise MusicImportError(
                f"Multiple albums match '{album_name}'. "
                "The import cannot safely determine which album to use."
            )

        if candidates:
            album = candidates[0]
            created = False
        else:
            album = Album.objects.create(
                title=album_name,
                slug=cls._unique_slug(Album, album_name),
                release_date=cls._parse_release_date(result.release_date),
            )
            created = True

        if artist is not None:
            album.artists.add(artist)

        cls._set_album_artwork(album=album, result=result)
        cls._publish_imported_album(album)

        identity = MusicProviderIdentity.objects.create(
            provider=result.provider,
            entity_type=result.entity_type,
            provider_id=result.provider_id,
            album=album,
            artwork_url=result.artwork_url or "",
            spotify_url=result.spotify_url or "",
            apple_music_url=result.apple_music_url or "",
            youtube_url=result.youtube_url or "",
            audiomack_url=result.audiomack_url or "",
            boomplay_url=result.boomplay_url or "",
            metadata=dict(result.metadata),
        )

        cls._sync_album_tracklist(album=album, result=result)

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
        existing_identity = cls._find_identity(result)

        if existing_identity:
            if not existing_identity.song:
                raise MusicImportError(
                    "The provider identity is not linked to a song."
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

        artist = cls._resolve_artist(result=result)
        album = cls._resolve_album(result=result, artist=artist)

        song_title = result.title.strip()

        if not song_title:
            raise MusicImportError(
                "The provider result does not contain a song title."
            )

        normalized_title = cls._normalized(song_title)

        candidates = [
            song
            for song in Song.objects.prefetch_related("artists")
            if cls._normalized(song.title) == normalized_title
            and song.artists.filter(pk=artist.pk).exists()
        ]

        if result.duration_seconds is not None:
            candidates = [
                song
                for song in candidates
                if (
                    song.duration_seconds is None
                    or abs(
                        song.duration_seconds - result.duration_seconds
                    ) <= 2
                )
            ]

        if len(candidates) > 1:
            raise MusicImportError(
                f"Multiple songs match '{song_title}' by '{artist.name}'. "
                "The import cannot safely determine which song to use."
            )

        if candidates:
            song = candidates[0]
            created = False
        else:
            song = Song.objects.create(
                title=song_title,
                slug=cls._unique_slug(
                    Song,
                    f"{song_title} {artist.name}",
                ),
                album=album,
                release_date=cls._parse_release_date(result.release_date),
                duration_seconds=result.duration_seconds,
                status=Song.Status.PUBLISHED,
                published_at=timezone.now(),
            )
            created = True

        song.artists.add(artist)

        if album is not None and song.album_id is None:
            song.album = album
            song.save(update_fields=["album", "updated_at"])

        cls._set_song_artwork(song=song, result=result)
        cls._attach_song_genres(song=song, result=result)

        identity = MusicProviderIdentity.objects.create(
            provider=result.provider,
            entity_type=result.entity_type,
            provider_id=result.provider_id,
            song=song,
            artwork_url=result.artwork_url or "",
            preview_url=result.preview_url or "",
            spotify_url=result.spotify_url or "",
            apple_music_url=result.apple_music_url or "",
            youtube_url=result.youtube_url or "",
            audiomack_url=result.audiomack_url or "",
            boomplay_url=result.boomplay_url or "",
            metadata=dict(result.metadata),
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
        """Import or resolve a provider result within a database transaction."""
        provider_id = (result.provider_id or "").strip()
        title = (result.title or "").strip()

        if not provider_id:
            raise MusicImportError(
                "Provider result is missing its provider ID."
            )

        if not title:
            raise MusicImportError(
                "Provider result is missing its title."
            )

        if result.entity_type == MusicEntityType.ARTIST:
            return cls._import_artist(result)

        if result.entity_type == MusicEntityType.ALBUM:
            return cls._import_album(result)

        if result.entity_type == MusicEntityType.SONG:
            return cls._import_song(result)

        raise MusicImportError(
            f"Unsupported music entity type: {result.entity_type}"
        )
