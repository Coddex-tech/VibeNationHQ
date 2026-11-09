
from unittest import TestCase
from unittest.mock import patch

from music.providers.base import (
    MusicEntityType,
    MusicProviderResponseError,
)
from music.providers.itunes import ITunesProvider


class ITunesGetAlbumTracksTests(TestCase):
    def setUp(self):
        self.provider = ITunesProvider()
        self.album_id = "12345"

    def album_result(self, *, track_count=3, collection_id=12345):
        return {
            "wrapperType": "collection",
            "collectionType": "Album",
            "collectionId": collection_id,
            "collectionName": "Test Album",
            "artistName": "Test Artist",
            "trackCount": track_count,
        }

    def track_result(
        self,
        *,
        track_id,
        track_number,
        disc_number=1,
        collection_id=12345,
    ):
        return {
            "wrapperType": "track",
            "kind": "song",
            "trackId": track_id,
            "trackName": f"Track {track_id}",
            "artistName": "Test Artist",
            "collectionId": collection_id,
            "collectionName": "Test Album",
            "trackNumber": track_number,
            "discNumber": disc_number,
            "trackTimeMillis": 180000,
        }

    def mock_lookup(self, results):
        return patch.object(
            self.provider,
            "_request",
            return_value={"results": results},
        )

    def test_returns_tracks_in_disc_and_track_order(self):
        response = [
            self.album_result(track_count=3),
            self.track_result(track_id=103, track_number=1, disc_number=2),
            self.track_result(track_id=102, track_number=2, disc_number=1),
            self.track_result(track_id=101, track_number=1, disc_number=1),
        ]

        with self.mock_lookup(response):
            tracks = self.provider.get_album_tracks(
                album_provider_id=self.album_id,
                country="NG",
            )

        self.assertEqual(
            [track.provider_id for track in tracks],
            ["101", "102", "103"],
        )
        self.assertTrue(
            all(track.entity_type == MusicEntityType.SONG for track in tracks)
        )
        self.assertEqual(
            [track.metadata["track_number"] for track in tracks],
            [1, 2, 1],
        )
        self.assertEqual(
            [track.metadata["disc_number"] for track in tracks],
            [1, 1, 2],
        )

    def test_requests_album_lookup_with_country_and_song_entity(self):
        with self.mock_lookup(
            [
                self.album_result(track_count=1),
                self.track_result(track_id=101, track_number=1),
            ]
        ) as request:
            self.provider.get_album_tracks(
                album_provider_id=self.album_id,
                country="NG",
            )

        request.assert_called_once_with(
            url=self.provider.LOOKUP_URL,
            params={
                "id": 12345,
                "entity": "song",
                "country": "NG",
            },
        )

    def test_rejects_empty_album_provider_id(self):
        with patch.object(self.provider, "_request") as request:
            with self.assertRaises(MusicProviderResponseError):
                self.provider.get_album_tracks(album_provider_id=" ")

        request.assert_not_called()

    def test_rejects_non_numeric_album_provider_id(self):
        with patch.object(self.provider, "_request") as request:
            with self.assertRaises(MusicProviderResponseError):
                self.provider.get_album_tracks(
                    album_provider_id="not-a-number"
                )

        request.assert_not_called()

    def test_rejects_non_positive_album_provider_id(self):
        for invalid_id in ("0", "-123"):
            with self.subTest(invalid_id=invalid_id):
                with patch.object(self.provider, "_request") as request:
                    with self.assertRaises(MusicProviderResponseError):
                        self.provider.get_album_tracks(
                            album_provider_id=invalid_id
                        )

                    request.assert_not_called()

    def test_rejects_malformed_results(self):
        with patch.object(
            self.provider,
            "_request",
            return_value={"results": None},
        ):
            with self.assertRaises(MusicProviderResponseError):
                self.provider.get_album_tracks(
                    album_provider_id=self.album_id
                )

    def test_rejects_response_without_requested_album(self):
        response = [
            self.album_result(collection_id=99999),
            self.track_result(
                track_id=101,
                track_number=1,
                collection_id=99999,
            ),
        ]

        with self.mock_lookup(response):
            with self.assertRaises(MusicProviderResponseError):
                self.provider.get_album_tracks(
                    album_provider_id=self.album_id
                )

    def test_rejects_empty_album_tracklist(self):
        with self.mock_lookup([self.album_result(track_count=3)]):
            with self.assertRaises(MusicProviderResponseError):
                self.provider.get_album_tracks(
                    album_provider_id=self.album_id
                )

    def test_rejects_incomplete_tracklist(self):
        response = [
            self.album_result(track_count=3),
            self.track_result(track_id=101, track_number=1),
            self.track_result(track_id=102, track_number=2),
        ]

        with self.mock_lookup(response):
            with self.assertRaisesRegex(
                MusicProviderResponseError,
                "incomplete album tracklist",
            ):
                self.provider.get_album_tracks(
                    album_provider_id=self.album_id
                )

    def test_rejects_invalid_album_track_count(self):
        response = [
            self.album_result(track_count=0),
            self.track_result(track_id=101, track_number=1),
        ]

        with self.mock_lookup(response):
            with self.assertRaises(MusicProviderResponseError):
                self.provider.get_album_tracks(
                    album_provider_id=self.album_id
                )

    def test_rejects_track_without_valid_track_number(self):
        invalid_track = self.track_result(
            track_id=101,
            track_number=0,
        )
        response = [
            self.album_result(track_count=1),
            invalid_track,
        ]

        with self.mock_lookup(response):
            with self.assertRaises(MusicProviderResponseError):
                self.provider.get_album_tracks(
                    album_provider_id=self.album_id
                )

    def test_rejects_invalid_disc_number(self):
        invalid_track = self.track_result(
            track_id=101,
            track_number=1,
            disc_number=0,
        )
        response = [
            self.album_result(track_count=1),
            invalid_track,
        ]

        with self.mock_lookup(response):
            with self.assertRaises(MusicProviderResponseError):
                self.provider.get_album_tracks(
                    album_provider_id=self.album_id
                )

    def test_rejects_duplicate_provider_track_ids(self):
        response = [
            self.album_result(track_count=2),
            self.track_result(track_id=101, track_number=1),
            self.track_result(track_id=101, track_number=2),
        ]

        with self.mock_lookup(response):
            with self.assertRaisesRegex(
                MusicProviderResponseError,
                "duplicate track IDs",
            ):
                self.provider.get_album_tracks(
                    album_provider_id=self.album_id
                )

    def test_rejects_duplicate_disc_and_track_positions(self):
        response = [
            self.album_result(track_count=2),
            self.track_result(track_id=101, track_number=1, disc_number=1),
            self.track_result(track_id=102, track_number=1, disc_number=1),
        ]

        with self.mock_lookup(response):
            with self.assertRaisesRegex(
                MusicProviderResponseError,
                "duplicate track positions",
            ):
                self.provider.get_album_tracks(
                    album_provider_id=self.album_id
                )

    def test_ignores_tracks_from_another_album(self):
        response = [
            self.album_result(track_count=1),
            self.track_result(
                track_id=101,
                track_number=1,
                collection_id=12345,
            ),
            self.track_result(
                track_id=999,
                track_number=2,
                collection_id=88888,
            ),
        ]

        with self.mock_lookup(response):
            tracks = self.provider.get_album_tracks(
                album_provider_id=self.album_id
            )

        self.assertEqual(len(tracks), 1)
        self.assertEqual(tracks[0].provider_id, "101")

    def test_accepts_album_without_track_count_metadata(self):
        album = self.album_result()
        album.pop("trackCount")

        response = [
            album,
            self.track_result(track_id=101, track_number=1),
        ]

        with self.mock_lookup(response):
            tracks = self.provider.get_album_tracks(
                album_provider_id=self.album_id
            )

        self.assertEqual(len(tracks), 1)
        self.assertEqual(tracks[0].provider_id, "101")
