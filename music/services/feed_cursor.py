from __future__ import annotations

import json
import secrets
from dataclasses import dataclass
from typing import Any

from django.core import signing
from django.core.cache import cache


@dataclass(frozen=True, slots=True)
class FeedSnapshotItem:
    content_type: str
    object_id: int
    source: str
    score: float


@dataclass(frozen=True, slots=True)
class FeedCursor:
    snapshot_id: str
    position: int


class FeedCursorError(ValueError):
    """Raised when a feed cursor cannot be used."""


class FeedSnapshotStore:
    """
    Stores the ordered result of a feed generation so subsequent
    cursor requests continue through the same feed snapshot.

    The cache backend can be LocMemCache during development and
    Redis in production without changing this service.
    """

    CURSOR_SALT = "music-feed-cursor"
    CACHE_PREFIX = "music:feed:snapshot:"
    SNAPSHOT_TTL = 60 * 15

    @classmethod
    def create_snapshot(
        cls,
        items: list[FeedSnapshotItem],
    ) -> str:
        snapshot_id = secrets.token_urlsafe(24)

        payload = [
            {
                "content_type": item.content_type,
                "object_id": item.object_id,
                "source": item.source,
                "score": item.score,
            }
            for item in items
        ]

        cache.set(
            cls._cache_key(snapshot_id),
            payload,
            timeout=cls.SNAPSHOT_TTL,
        )

        return snapshot_id

    @classmethod
    def get_snapshot(
        cls,
        snapshot_id: str,
    ) -> list[FeedSnapshotItem]:
        payload = cache.get(
            cls._cache_key(snapshot_id),
        )

        if payload is None:
            raise FeedCursorError(
                "This feed has expired. Please refresh "
                "the feed and try again."
            )

        if not isinstance(payload, list):
            raise FeedCursorError(
                "The feed snapshot is invalid."
            )

        items: list[FeedSnapshotItem] = []

        for item in payload:
            if not isinstance(item, dict):
                raise FeedCursorError(
                    "The feed snapshot is invalid."
                )

            try:
                items.append(
                    FeedSnapshotItem(
                        content_type=str(
                            item["content_type"],
                        ),
                        object_id=int(
                            item["object_id"],
                        ),
                        source=str(item["source"]),
                        score=float(item["score"]),
                    )
                )
            except (
                KeyError,
                TypeError,
                ValueError,
            ) as exc:
                raise FeedCursorError(
                    "The feed snapshot is invalid."
                ) from exc

        return items

    @classmethod
    def create_cursor(
        cls,
        *,
        snapshot_id: str,
        position: int,
    ) -> str:
        if position < 0:
            raise ValueError(
                "Cursor position cannot be negative."
            )

        payload = {
            "snapshot_id": snapshot_id,
            "position": position,
        }

        return signing.dumps(
            payload,
            salt=cls.CURSOR_SALT,
        )

    @classmethod
    def decode_cursor(
        cls,
        value: str,
    ) -> FeedCursor:
        if not value:
            raise FeedCursorError(
                "Feed cursor is required."
            )

        try:
            payload: Any = signing.loads(
                value,
                salt=cls.CURSOR_SALT,
                max_age=cls.SNAPSHOT_TTL,
            )
        except signing.BadSignature as exc:
            raise FeedCursorError(
                "This feed cursor is invalid or has expired."
            ) from exc

        if not isinstance(payload, dict):
            raise FeedCursorError(
                "This feed cursor is invalid."
            )

        try:
            snapshot_id = str(
                payload["snapshot_id"],
            )
            position = int(
                payload["position"],
            )
        except (
            KeyError,
            TypeError,
            ValueError,
        ) as exc:
            raise FeedCursorError(
                "This feed cursor is invalid."
            ) from exc

        if not snapshot_id or position < 0:
            raise FeedCursorError(
                "This feed cursor is invalid."
            )

        return FeedCursor(
            snapshot_id=snapshot_id,
            position=position,
        )

    @classmethod
    def delete_snapshot(
        cls,
        snapshot_id: str,
    ) -> None:
        cache.delete(
            cls._cache_key(snapshot_id),
        )

    @classmethod
    def _cache_key(
        cls,
        snapshot_id: str,
    ) -> str:
        return f"{cls.CACHE_PREFIX}{snapshot_id}"