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
from music.providers.itunes import ITunesProvider


class ITunesProviderTests(SimpleTestCase):
    def setUp(self):
        self.provider = ITunesProvider()

    def make_song_item(
        self,
        **overrides,
    ) -> dict:
        item = {
            "wrapperType": "track",
            "kind": "song",
            "artistId": 123,
            "collectionId": 456,
            "trackId": 789,
            "artistName": "Rema",
            "collectionName": "HEIS",
            "trackName": "Calm Down",
            "artworkUrl100": (
                "https://example.com/100x100bb.jpg"
            ),
            "releaseDate": "2022-02-11T00:00:00Z",
            "trackTimeMillis": 239000,
            "previewUrl": (
                "https://example.com/preview.m4a"
            ),
            "trackViewUrl": (
                "https://music.apple.com/song/789"
            ),
            "country": "Nigeria",
            "isrc": "NGABC2200001",
            "primaryGenreName": "Afrobeats",
            "trackNumber": 1,
            "trackCount": 17,
        }

        item.update(overrides)
        return item

    def make_album_item(
        self,
        **overrides,
    ) -> dict:
        item = {
            "wrapperType": "collection",
            "collectionType": "Album",
            "collectionId": 456,
            "artistId": 123,
            "artistName": "Rema",
            "collectionName": "HEIS",
            "artworkUrl100": (
                "https://example.com/100x100bb.jpg"
            ),
            "releaseDate": "2024-07-11T00:00:00Z",
            "collectionViewUrl": (
                "https://music.apple.com/album/456"
            ),
            "country": "Nigeria",
            "primaryGenreName": "Afrobeats",
        }

        item.update(overrides)
        return item

    def make_artist_item(
        self,
        **overrides,
    ) -> dict:
        item = {
            "wrapperType": "artist",
            "artistType": "Artist",
            "artistId": 123,
            "artistName": "Rema",
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
            self.make_song_item()
        )

        self.assertIsNotNone(result)

        assert result is not None

        self.assertEqual(
            result.provider,
            MusicProviderName.ITUNES,
        )
        self.assertEqual(
            result.provider_id,
            "789",
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
            "HEIS",
        )

    def test_extracts_primary_genre_name_into_metadata(self):
        result = self.provider._normalize_result(
            self.make_song_item(
                primaryGenreName="Afrobeats"
            )
        )

        self.assertIsNotNone(result)

        assert result is not None

        self.assertEqual(
            result.metadata["primary_genre_name"],
            "Afrobeats",
        )

    def test_cleans_primary_genre_name(self):
        result = self.provider._normalize_result(
            self.make_song_item(
                primaryGenreName="  Afrobeats  "
            )
        )

        self.assertIsNotNone(result)

        assert result is not None

        self.assertEqual(
            result.metadata["primary_genre_name"],
            "Afrobeats",
        )

    def test_omits_blank_primary_genre_name(self):
        result = self.provider._normalize_result(
            self.make_song_item(
                primaryGenreName="   "
            )
        )

        self.assertIsNotNone(result)

        assert result is not None

        self.assertNotIn(
            "primary_genre_name",
            result.metadata,
        )

    def test_omits_non_string_primary_genre_name(self):
        result = self.provider._normalize_result(
            self.make_song_item(
                primaryGenreName=123
            )
        )

        self.assertIsNotNone(result)

        assert result is not None

        self.assertNotIn(
            "primary_genre_name",
            result.metadata,
        )

    def test_normalizes_album_result(self):
        result = self.provider._normalize_result(
            self.make_album_item()
        )

        self.assertIsNotNone(result)

        assert result is not None

        self.assertEqual(
            result.provider_id,
            "456",
        )
        self.assertEqual(
            result.entity_type,
            MusicEntityType.ALBUM,
        )
        self.assertEqual(
            result.title,
            "HEIS",
        )
        self.assertEqual(
            result.metadata["primary_genre_name"],
            "Afrobeats",
        )

    def test_normalizes_artist_result(self):
        result = self.provider._normalize_result(
            self.make_artist_item()
        )

        self.assertIsNotNone(result)

        assert result is not None

        self.assertEqual(
            result.provider_id,
            "123",
        )
        self.assertEqual(
            result.entity_type,
            MusicEntityType.ARTIST,
        )
        self.assertEqual(
            result.title,
            "Rema",
        )

    def test_normalizes_artwork_to_600_by_600(self):
        result = self.provider._normalize_result(
            self.make_song_item()
        )

        self.assertIsNotNone(result)

        assert result is not None

        self.assertEqual(
            result.artwork_url,
            "https://example.com/600x600bb.jpg",
        )

    def test_normalizes_duration_to_seconds(self):
        result = self.provider._normalize_result(
            self.make_song_item(
                trackTimeMillis=239500
            )
        )

        self.assertIsNotNone(result)

        assert result is not None

        self.assertEqual(
            result.duration_seconds,
            240,
        )

    def test_normalizes_release_date(self):
        result = self.provider._normalize_result(
            self.make_song_item(
                releaseDate="2022-02-11T12:34:56Z"
            )
        )

        self.assertIsNotNone(result)

        assert result is not None

        self.assertEqual(
            result.release_date,
            "2022-02-11",
        )

    def test_search_returns_normalized_results(self):
        response = self.make_response(
            {
                "resultCount": 1,
                "results": [
                    self.make_song_item()
                ],
            }
        )

        with patch(
            "music.providers.itunes.urlopen",
            return_value=response,
        ):
            results = self.provider.search(
                MusicSearchQuery(
                    query="Rema Calm Down",
                    entity_type=MusicEntityType.SONG,
                    country="NG",
                    limit=10,
                )
            )

        self.assertEqual(
            len(results),
            1,
        )

        self.assertEqual(
            results[0].entity_type,
            MusicEntityType.SONG,
        )

        self.assertEqual(
            results[0].metadata[
                "primary_genre_name"
            ],
            "Afrobeats",
        )

    def test_search_clamps_limit_to_50(self):
        response = self.make_response(
            {
                "resultCount": 0,
                "results": [],
            }
        )

        with patch(
            "music.providers.itunes.urlopen",
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
            "limit=50",
            request.full_url,
        )

    def test_search_returns_empty_for_blank_query(
        self,
    ):
        with patch(
            "music.providers.itunes.urlopen"
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

    def test_get_returns_matching_song(self):
        response = self.make_response(
            {
                "resultCount": 1,
                "results": [
                    self.make_song_item()
                ],
            }
        )

        with patch(
            "music.providers.itunes.urlopen",
            return_value=response,
        ):
            result = self.provider.get(
                entity_type=MusicEntityType.SONG,
                provider_id="789",
                country="NG",
            )

        self.assertIsNotNone(result)

        assert result is not None

        self.assertEqual(
            result.provider_id,
            "789",
        )
        self.assertEqual(
            result.metadata[
                "primary_genre_name"
            ],
            "Afrobeats",
        )

    def test_get_returns_none_when_entity_type_does_not_match(
        self,
    ):
        response = self.make_response(
            {
                "resultCount": 1,
                "results": [
                    self.make_song_item()
                ],
            }
        )

        with patch(
            "music.providers.itunes.urlopen",
            return_value=response,
        ):
            result = self.provider.get(
                entity_type=MusicEntityType.ALBUM,
                provider_id="789",
            )

        self.assertIsNone(result)

    def test_get_returns_none_for_blank_provider_id(
        self,
    ):
        with patch(
            "music.providers.itunes.urlopen"
        ) as mocked_urlopen:
            result = self.provider.get(
                entity_type=MusicEntityType.SONG,
                provider_id="   ",
            )

        self.assertIsNone(result)

        mocked_urlopen.assert_not_called()

    def test_get_rejects_non_numeric_provider_id(self):
        with self.assertRaises(
            MusicProviderResponseError
        ):
            self.provider.get(
                entity_type=MusicEntityType.SONG,
                provider_id="abc",
            )

    def test_search_rejects_invalid_response_shape(
        self,
    ):
        response = self.make_response(
            {
                "resultCount": 1,
                "results": {},
            }
        )

        with patch(
            "music.providers.itunes.urlopen",
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

    def test_request_handles_rate_limit(self):
        error = HTTPError(
            url="https://itunes.apple.com/search",
            code=429,
            msg="Too Many Requests",
            hdrs=None,
            fp=None,
        )

        with patch(
            "music.providers.itunes.urlopen",
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
            "music.providers.itunes.urlopen",
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
            "music.providers.itunes.urlopen",
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

    def test_normalize_result_returns_none_without_provider_id(
        self,
    ):
        item = self.make_song_item(
            trackId=None
        )

        result = self.provider._normalize_result(
            item
        )

        self.assertIsNone(result)

    def test_normalize_result_returns_none_without_title(
        self,
    ):
        item = self.make_song_item(
            trackName="   "
        )

        result = self.provider._normalize_result(
            item
        )

        self.assertIsNone(result)

    def test_unsupported_entity_type_raises_provider_error(
        self,
    ):
        with self.assertRaises(
            MusicProviderError
        ):
            self.provider._get_entity(
                object()
            )