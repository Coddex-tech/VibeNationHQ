from __future__ import annotations

import json
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError, URLError

from django.test import SimpleTestCase

from music.providers.base import (
    MusicEntityType,
    MusicProviderError,
    MusicProviderName,
    MusicProviderResponseError,
    MusicProviderUnavailableError,
    MusicSearchQuery,
)
from music.providers.musicbrainz import MusicBrainzProvider


class MusicBrainzProviderTests(SimpleTestCase):
    def setUp(self):
        self.provider = MusicBrainzProvider()

    def make_song_item(
        self,
        **overrides,
    ) -> dict:
        item = {
            "id": "song-mbid-123",
            "title": "Calm Down",
            "score": 100,
            "video": False,
            "first-release-date": "2022-02-11",
            "disambiguation": "",
            "length": 239000,
            "artist-credit": [
                {
                    "artist": {
                        "id": "artist-mbid-123",
                        "name": "Rema",
                    },
                    "joinphrase": "",
                }
            ],
            "isrcs": [
                "NGABC2200001",
            ],
            "releases": [
                {
                    "id": "release-mbid-123",
                    "title": "Rave & Roses",
                    "date": "2022-02-11",
                }
            ],
            "genres": [
                {
                    "name": "Afrobeats",
                    "count": 5,
                },
                {
                    "name": "Pop",
                    "count": 2,
                },
            ],
            "tags": [
                {
                    "name": "afrobeats",
                    "count": 5,
                },
            ],
        }

        item.update(overrides)
        return item

    def make_album_item(
        self,
        **overrides,
    ) -> dict:
        item = {
            "id": "album-mbid-123",
            "title": "Rave & Roses",
            "score": 100,
            "first-release-date": "2022-03-25",
            "primary-type": "Album",
            "secondary-types": [],
            "disambiguation": "",
            "artist-credit": [
                {
                    "artist": {
                        "id": "artist-mbid-123",
                        "name": "Rema",
                    },
                    "joinphrase": "",
                }
            ],
            "genres": [
                {
                    "name": "Afrobeats",
                    "count": 5,
                }
            ],
            "tags": [],
        }

        item.update(overrides)
        return item

    def make_artist_item(
        self,
        **overrides,
    ) -> dict:
        item = {
            "id": "artist-mbid-123",
            "name": "Rema",
            "sort-name": "Rema",
            "type": "Person",
            "country": "NG",
            "area": {
                "name": "Nigeria",
            },
            "disambiguation": "",
            "genres": [
                {
                    "name": "Afrobeats",
                    "count": 10,
                }
            ],
            "tags": [],
        }

        item.update(overrides)
        return item

    def make_response(
        self,
        payload: dict,
    ):
        response = MagicMock()
        response.read.return_value = json.dumps(
            payload
        ).encode("utf-8")
        response.__enter__.return_value = response
        response.__exit__.return_value = False

        return response

    def test_normalizes_song_result(self):
        result = self.provider._normalize_result(
            item=self.make_song_item(),
            entity_type=MusicEntityType.SONG,
        )

        self.assertIsNotNone(result)

        assert result is not None

        self.assertEqual(
            result.provider,
            MusicProviderName.MUSICBRAINZ,
        )
        self.assertEqual(
            result.provider_id,
            "song-mbid-123",
        )
        self.assertEqual(
            result.entity_type,
            MusicEntityType.SONG,
        )
        self.assertEqual(
            result.title,
            "Calm Down",
        )
        self.assertEqual(
            result.artist_name,
            "Rema",
        )
        self.assertEqual(
            result.album_name,
            "Rave & Roses",
        )
        self.assertEqual(
            result.isrc,
            "NGABC2200001",
        )

    def test_extracts_song_genres(self):
        result = self.provider._normalize_result(
            item=self.make_song_item(),
            entity_type=MusicEntityType.SONG,
        )

        self.assertIsNotNone(result)

        assert result is not None

        self.assertEqual(
            result.metadata["genres"],
            [
                "Afrobeats",
                "Pop",
            ],
        )

    def test_deduplicates_genres_case_insensitively(
        self,
    ):
        result = self.provider._normalize_result(
            item=self.make_song_item(
                genres=[
                    {
                        "name": "Afrobeats",
                        "count": 5,
                    },
                    {
                        "name": "afrobeats",
                        "count": 2,
                    },
                    {
                        "name": "Pop",
                        "count": 1,
                    },
                ]
            ),
            entity_type=MusicEntityType.SONG,
        )

        self.assertIsNotNone(result)

        assert result is not None

        self.assertEqual(
            result.metadata["genres"],
            [
                "Afrobeats",
                "Pop",
            ],
        )

    def test_ignores_invalid_genre_entries(self):
        result = self.provider._normalize_result(
            item=self.make_song_item(
                genres=[
                    {
                        "name": "Afrobeats"
                    },
                    {},
                    "Pop",
                    {
                        "name": "   "
                    },
                    {
                        "name": 123
                    },
                ]
            ),
            entity_type=MusicEntityType.SONG,
        )

        self.assertIsNotNone(result)

        assert result is not None

        self.assertEqual(
            result.metadata["genres"],
            ["Afrobeats"],
        )

    def test_falls_back_to_tags_when_genres_are_missing(
        self,
    ):
        result = self.provider._normalize_result(
            item=self.make_song_item(
                genres=[],
                tags=[
                    {
                        "name": "Afrobeats",
                        "count": 5,
                    },
                    {
                        "name": "Nigerian music",
                        "count": 2,
                    },
                ],
            ),
            entity_type=MusicEntityType.SONG,
        )

        self.assertIsNotNone(result)

        assert result is not None

        self.assertEqual(
            result.metadata["genres"],
            [
                "Afrobeats",
                "Nigerian music",
            ],
        )

    def test_omits_genres_when_no_genres_or_tags_exist(self):
        payload = {
            "id": "song-123",
            "title": "Test Song",
            "length": 180000,
            "first-release-date": "2022-02-11",
            "artist-credit": [
                {
                    "artist": {
                        "id": "artist-123",
                        "name": "Test Artist",
                    }
                }
            ],
            "releases": [],
            "isrcs": [],
        }

        result = self.provider._normalize_song(payload)

        self.assertEqual(
            result.metadata.get("genres"),
            [],
        )

    def test_normalizes_album_genres(self):
        result = self.provider._normalize_result(
            item=self.make_album_item(),
            entity_type=MusicEntityType.ALBUM,
        )

        self.assertIsNotNone(result)

        assert result is not None

        self.assertEqual(
            result.entity_type,
            MusicEntityType.ALBUM,
        )
        self.assertEqual(
            result.metadata["genres"],
            ["Afrobeats"],
        )

    def test_normalizes_artist_genres(self):
        result = self.provider._normalize_result(
            item=self.make_artist_item(),
            entity_type=MusicEntityType.ARTIST,
        )

        self.assertIsNotNone(result)

        assert result is not None

        self.assertEqual(
            result.entity_type,
            MusicEntityType.ARTIST,
        )
        self.assertEqual(
            result.metadata["genres"],
            ["Afrobeats"],
        )

    def test_normalizes_duration(self):
        result = self.provider._normalize_result(
            item=self.make_song_item(
                length=239500
            ),
            entity_type=MusicEntityType.SONG,
        )

        self.assertIsNotNone(result)

        assert result is not None

        self.assertEqual(
            result.duration_seconds,
            240,
        )

    def test_search_returns_normalized_results(self):
        response = self.make_response(
            {
                "count": 1,
                "recordings": [
                    self.make_song_item()
                ],
            }
        )

        with patch(
            "music.providers.musicbrainz.urlopen",
            return_value=response,
        ):
            results = self.provider.search(
                MusicSearchQuery(
                    query="Rema Calm Down",
                    entity_type=MusicEntityType.SONG,
                    limit=10,
                )
            )

        self.assertEqual(
            len(results),
            1,
        )

        self.assertEqual(
            results[0].title,
            "Calm Down",
        )

        self.assertEqual(
            results[0].metadata["genres"],
            [
                "Afrobeats",
                "Pop",
            ],
        )

    def test_search_clamps_limit_to_25(self):
        response = self.make_response(
            {
                "count": 0,
                "recordings": [],
            }
        )

        with patch(
            "music.providers.musicbrainz.urlopen",
            return_value=response,
        ) as mocked_urlopen:
            self.provider.search(
                MusicSearchQuery(
                    query="Rema",
                    limit=1000,
                )
            )

        request = mocked_urlopen.call_args.args[0]

        self.assertIn(
            "limit=25",
            request.full_url,
        )

    def test_search_returns_empty_for_blank_query(
        self,
    ):
        with patch(
            "music.providers.musicbrainz.urlopen"
        ) as mocked_urlopen:
            results = self.provider.search(
                MusicSearchQuery(
                    query="   "
                )
            )

        self.assertEqual(
            results,
            [],
        )

        mocked_urlopen.assert_not_called()

    def test_get_returns_song_with_genres(self):
        response = self.make_response(
            self.make_song_item()
        )

        with patch(
            "music.providers.musicbrainz.urlopen",
            return_value=response,
        ) as mocked_urlopen:
            result = self.provider.get(
                entity_type=MusicEntityType.SONG,
                provider_id="song-mbid-123",
            )

        self.assertIsNotNone(result)

        assert result is not None

        self.assertEqual(
            result.metadata["genres"],
            [
                "Afrobeats",
                "Pop",
            ],
        )

        request = mocked_urlopen.call_args.args[0]

        self.assertIn(
            "genres",
            request.full_url,
        )

        self.assertIn(
            "tags",
            request.full_url,
        )

    def test_get_returns_album_with_genres(self):
        response = self.make_response(
            self.make_album_item()
        )

        with patch(
            "music.providers.musicbrainz.urlopen",
            return_value=response,
        ):
            result = self.provider.get(
                entity_type=MusicEntityType.ALBUM,
                provider_id="album-mbid-123",
            )

        self.assertIsNotNone(result)

        assert result is not None

        self.assertEqual(
            result.metadata["genres"],
            ["Afrobeats"],
        )

    def test_get_returns_artist_with_genres(self):
        response = self.make_response(
            self.make_artist_item()
        )

        with patch(
            "music.providers.musicbrainz.urlopen",
            return_value=response,
        ):
            result = self.provider.get(
                entity_type=MusicEntityType.ARTIST,
                provider_id="artist-mbid-123",
            )

        self.assertIsNotNone(result)

        assert result is not None

        self.assertEqual(
            result.metadata["genres"],
            ["Afrobeats"],
        )

    def test_get_returns_none_for_blank_provider_id(
        self,
    ):
        with patch(
            "music.providers.musicbrainz.urlopen"
        ) as mocked_urlopen:
            result = self.provider.get(
                entity_type=MusicEntityType.SONG,
                provider_id="   ",
            )

        self.assertIsNone(result)

        mocked_urlopen.assert_not_called()

    def test_request_handles_rate_limit(self):
        error = HTTPError(
            url="https://musicbrainz.org/ws/2/recording",
            code=429,
            msg="Too Many Requests",
            hdrs=None,
            fp=None,
        )

        with patch(
            "music.providers.musicbrainz.urlopen",
            side_effect=error,
        ):
            with self.assertRaises(
                MusicProviderUnavailableError
            ):
                self.provider.search(
                    MusicSearchQuery(
                        query="Rema"
                    )
                )

    def test_request_handles_connection_error(self):
        with patch(
            "music.providers.musicbrainz.urlopen",
            side_effect=URLError(
                "Connection failed"
            ),
        ):
            with self.assertRaises(
                MusicProviderUnavailableError
            ):
                self.provider.search(
                    MusicSearchQuery(
                        query="Rema"
                    )
                )

    def test_request_handles_invalid_json(self):
        response = MagicMock()
        response.read.return_value = (
            b"not-valid-json"
        )
        response.__enter__.return_value = response
        response.__exit__.return_value = False

        with patch(
            "music.providers.musicbrainz.urlopen",
            return_value=response,
        ):
            with self.assertRaises(
                MusicProviderResponseError
            ):
                self.provider.search(
                    MusicSearchQuery(
                        query="Rema"
                    )
                )

    def test_search_rejects_invalid_response_shape(
        self,
    ):
        response = self.make_response(
            {
                "count": 1,
                "recordings": {},
            }
        )

        with patch(
            "music.providers.musicbrainz.urlopen",
            return_value=response,
        ):
            with self.assertRaises(
                MusicProviderResponseError
            ):
                self.provider.search(
                    MusicSearchQuery(
                        query="Rema"
                    )
                )

    def test_normalize_song_returns_none_without_id(
        self,
    ):
        result = self.provider._normalize_result(
            item=self.make_song_item(
                id=None
            ),
            entity_type=MusicEntityType.SONG,
        )

        self.assertIsNone(result)

    def test_normalize_song_returns_none_without_title(
        self,
    ):
        result = self.provider._normalize_result(
            item=self.make_song_item(
                title="   "
            ),
            entity_type=MusicEntityType.SONG,
        )

        self.assertIsNone(result)

    def test_unsupported_entity_type_raises_provider_error(
        self,
    ):
        with self.assertRaises(
            MusicProviderError
        ):
            self.provider._get_endpoint(
                object()
            )