from __future__ import annotations

from rest_framework import serializers

from music.models import (
    Album,
    Artist,
    Song,
)
from music.providers.base import (
    MusicEntityType,
    MusicProviderName,
    MusicSearchResult,
)


class MusicProviderImportSerializer(
    serializers.Serializer,
):
    """
    Validates an external provider result before it is
    passed to MusicProviderImportService.

    Importing is explicit: simply searching a provider
    never creates canonical catalog records.
    """

    provider = serializers.ChoiceField(
        choices=[
            provider.value
            for provider in MusicProviderName
        ],
    )

    provider_id = serializers.CharField(
        max_length=255,
    )

    entity_type = serializers.ChoiceField(
        choices=[
            entity_type.value
            for entity_type in MusicEntityType
        ],
    )

    title = serializers.CharField(
        max_length=250,
    )

    artist_name = serializers.CharField(
        max_length=200,
        required=False,
        allow_null=True,
        allow_blank=True,
    )

    album_name = serializers.CharField(
        max_length=250,
        required=False,
        allow_null=True,
        allow_blank=True,
    )

    artwork_url = serializers.URLField(
        required=False,
        allow_null=True,
        allow_blank=True,
    )

    release_date = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
    )

    duration_seconds = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=0,
    )

    preview_url = serializers.URLField(
        required=False,
        allow_null=True,
        allow_blank=True,
    )

    spotify_url = serializers.URLField(
        required=False,
        allow_null=True,
        allow_blank=True,
    )

    apple_music_url = serializers.URLField(
        required=False,
        allow_null=True,
        allow_blank=True,
    )

    youtube_url = serializers.URLField(
        required=False,
        allow_null=True,
        allow_blank=True,
    )

    audiomack_url = serializers.URLField(
        required=False,
        allow_null=True,
        allow_blank=True,
    )

    boomplay_url = serializers.URLField(
        required=False,
        allow_null=True,
        allow_blank=True,
    )

    country = serializers.CharField(
        max_length=2,
        required=False,
        allow_null=True,
        allow_blank=True,
    )

    isrc = serializers.CharField(
        max_length=50,
        required=False,
        allow_null=True,
        allow_blank=True,
    )

    metadata = serializers.JSONField(
        required=False,
        default=dict,
    )

    @staticmethod
    def _normalize_optional_text(
        value: str | None,
    ) -> str | None:
        """
        Normalize optional text values.

        Empty or whitespace-only values become None.
        Non-empty values are stripped.
        """

        if value is None:
            return None

        value = value.strip()

        return value or None

    def validate_provider(
        self,
        value: str,
    ) -> str:
        return value.strip().lower()

    def validate_entity_type(
        self,
        value: str,
    ) -> str:
        return value.strip().lower()

    def validate_provider_id(
        self,
        value: str,
    ) -> str:
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Provider ID is required."
            )

        return value

    def validate_title(
        self,
        value: str,
    ) -> str:
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Title is required."
            )

        return value

    def validate_artist_name(
        self,
        value: str | None,
    ) -> str | None:
        return self._normalize_optional_text(value)

    def validate_album_name(
        self,
        value: str | None,
    ) -> str | None:
        return self._normalize_optional_text(value)

    def validate_artwork_url(
        self,
        value: str | None,
    ) -> str | None:
        return self._normalize_optional_text(value)

    def validate_release_date(
        self,
        value: str | None,
    ) -> str | None:
        return self._normalize_optional_text(value)

    def validate_preview_url(
        self,
        value: str | None,
    ) -> str | None:
        return self._normalize_optional_text(value)

    def validate_spotify_url(
        self,
        value: str | None,
    ) -> str | None:
        return self._normalize_optional_text(value)

    def validate_apple_music_url(
        self,
        value: str | None,
    ) -> str | None:
        return self._normalize_optional_text(value)

    def validate_youtube_url(
        self,
        value: str | None,
    ) -> str | None:
        return self._normalize_optional_text(value)

    def validate_audiomack_url(
        self,
        value: str | None,
    ) -> str | None:
        return self._normalize_optional_text(value)

    def validate_boomplay_url(
        self,
        value: str | None,
    ) -> str | None:
        return self._normalize_optional_text(value)

    def validate_country(
        self,
        value: str | None,
    ) -> str | None:
        value = self._normalize_optional_text(value)

        if value is None:
            return None

        value = value.upper()

        if len(value) != 2:
            raise serializers.ValidationError(
                "Country must be a 2-letter country code."
            )

        return value

    def validate_isrc(
        self,
        value: str | None,
    ) -> str | None:
        return self._normalize_optional_text(value)

    def validate_metadata(
        self,
        value,
    ) -> dict:
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Metadata must be an object."
            )

        return value

    def to_music_search_result(
        self,
    ) -> MusicSearchResult:
        """
        Convert validated request data into the provider
        result object expected by the import service.
        """

        if not hasattr(self, "_validated_data"):
            raise RuntimeError(
                "Call is_valid() before converting "
                "the request to a MusicSearchResult."
            )

        data = self.validated_data

        return MusicSearchResult(
            provider=MusicProviderName(
                data["provider"],
            ),
            provider_id=data["provider_id"],
            entity_type=MusicEntityType(
                data["entity_type"],
            ),
            title=data["title"],
            artist_name=data.get("artist_name"),
            album_name=data.get("album_name"),
            artwork_url=data.get("artwork_url"),
            release_date=data.get("release_date"),
            duration_seconds=data.get(
                "duration_seconds",
            ),
            preview_url=data.get("preview_url"),
            spotify_url=data.get("spotify_url"),
            apple_music_url=data.get(
                "apple_music_url",
            ),
            youtube_url=data.get("youtube_url"),
            audiomack_url=data.get("audiomack_url"),
            boomplay_url=data.get("boomplay_url"),
            country=data.get("country"),
            isrc=data.get("isrc"),
            metadata=data.get("metadata", {}),
        )


class MusicProviderImportResponseSerializer(
    serializers.Serializer,
):
    """
    Normalized response returned after a successful
    provider import.
    """

    entity_type = serializers.CharField()
    created = serializers.BooleanField()
    identity_id = serializers.IntegerField()
    object_id = serializers.IntegerField()
    object_type = serializers.CharField()
    title = serializers.CharField()
    artist = serializers.SerializerMethodField()
    album = serializers.SerializerMethodField()
    song = serializers.SerializerMethodField()

    def get_artist(self, result):
        if result.entity_type == MusicEntityType.ARTIST:
            artist = result.object
        elif result.entity_type == MusicEntityType.SONG:
            artist = result.object.artists.first()
        elif result.entity_type == MusicEntityType.ALBUM:
            artist = result.object.artists.first()
        else:
            artist = None

        if artist is None:
            return None

        return {
            "id": artist.id,
            "name": artist.name,
            "slug": artist.slug,
        }

    def get_album(self, result):
        if result.entity_type == MusicEntityType.ALBUM:
            album = result.object
        elif result.entity_type == MusicEntityType.SONG:
            album = result.object.album
        else:
            album = None

        if album is None:
            return None

        return {
            "id": album.id,
            "title": album.title,
            "slug": album.slug,
        }

    def get_song(self, result):
        if result.entity_type != MusicEntityType.SONG:
            return None

        song = result.object

        return {
            "id": song.id,
            "title": song.title,
            "slug": song.slug,
        }

    def to_representation(
        self,
        result,
    ):
        object_type = result.entity_type.value
        obj = result.object

        if isinstance(obj, Song):
            title = obj.title
        elif isinstance(obj, Album):
            title = obj.title
        elif isinstance(obj, Artist):
            title = obj.name
        else:
            title = str(obj)

        return {
            "entity_type": object_type,
            "created": result.created,
            "identity_id": result.identity.id,
            "object_id": result.object.id,
            "object_type": object_type,
            "title": title,
            "artist": self.get_artist(result),
            "album": self.get_album(result),
            "song": self.get_song(result),
        }