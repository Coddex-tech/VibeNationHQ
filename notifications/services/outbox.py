from __future__ import annotations

import uuid

from datetime import timedelta

from django.db import transaction
from django.db.models import Q, F
from django.utils import timezone

from notifications.models import NotificationOutbox


class NotificationOutboxService:
    """
    Manages reliable claiming and lifecycle of notification outbox jobs.

    This service does not send push notifications itself.

    It claims jobs for background processing and safely tracks
    completion, retries, expired leases, and terminal failures.
    """

    DEFAULT_BATCH_SIZE = 50
    DEFAULT_LEASE_SECONDS = 120

    BASE_RETRY_DELAY_SECONDS = 30
    MAX_RETRY_DELAY_SECONDS = 3600

    MAX_ERROR_LENGTH = 5000

    # ========================================================
    # CLAIM OUTBOX RECORDS
    # ========================================================

    @classmethod
    def claim_pending(
        cls,
        *,
        batch_size: int = DEFAULT_BATCH_SIZE,
        lease_seconds: int = DEFAULT_LEASE_SECONDS,
    ) -> list[NotificationOutbox]:
        """
        Atomically claim eligible outbox records.

        Eligible records:
        - Pending records whose available_at has arrived.
        - Processing records whose worker lease has expired.

        Records that have exhausted their maximum attempts
        are marked as permanently failed.

        Each claimed record receives a new ownership token.
        """

        if batch_size < 1:
            raise ValueError("batch_size must be at least 1.")

        if lease_seconds < 1:
            raise ValueError("lease_seconds must be at least 1.")

        now = timezone.now()
        lease_expiration = now + timedelta(
            seconds=lease_seconds,
        )

        with transaction.atomic():
            eligible = (
                Q(
                    status=NotificationOutbox.Status.PENDING,
                    available_at__lte=now,
                )
                | Q(
                    status=NotificationOutbox.Status.PROCESSING,
                    locked_until__lte=now,
                )
            )

            # Permanently fail records that have exhausted
            # their attempts, including abandoned processing jobs.
            (
                NotificationOutbox.objects
                .filter(eligible)
                .filter(attempts__gte=F("max_attempts"))
                .update(
                    status=NotificationOutbox.Status.FAILED,
                    locked_at=None,
                    locked_until=None,
                    lock_token=None,
                    last_error=(
                        "Maximum processing attempts exceeded."
                    ),
                )
            )

            records = list(
                NotificationOutbox.objects
                .select_for_update(skip_locked=True)
                .filter(eligible)
                .filter(
                    attempts__lt=F("max_attempts")
                )
                .order_by("available_at", "pk")[:batch_size]
            )

            for record in records:
                record.status = NotificationOutbox.Status.PROCESSING
                record.attempts += 1
                record.locked_at = now
                record.locked_until = lease_expiration
                record.lock_token = uuid.uuid4()

                record.save(
                    update_fields=[
                        "status",
                        "attempts",
                        "locked_at",
                        "locked_until",
                        "lock_token",
                        "updated_at",
                    ]
                )

            return records

    # ========================================================
    # COMPLETE OUTBOX RECORD
    # ========================================================

    @classmethod
    def mark_processed(
        cls,
        *,
        outbox_id: int,
        lock_token: uuid.UUID,
    ) -> bool:
        """
        Mark a claimed record as successfully processed.

        Only the worker holding the current lock token
        can complete the record.

        Returns False if the lease has been replaced or
        the record is no longer being processed.
        """

        now = timezone.now()

        with transaction.atomic():
            record = (
                NotificationOutbox.objects
                .select_for_update()
                .filter(
                    pk=outbox_id,
                    status=NotificationOutbox.Status.PROCESSING,
                    lock_token=lock_token,
                )
                .first()
            )

            if record is None:
                return False

            record.status = NotificationOutbox.Status.PROCESSED
            record.processed_at = now
            record.locked_at = None
            record.locked_until = None
            record.lock_token = None
            record.last_error = ""

            record.save(
                update_fields=[
                    "status",
                    "processed_at",
                    "locked_at",
                    "locked_until",
                    "lock_token",
                    "last_error",
                    "updated_at",
                ]
            )

            return True

    # ========================================================
    # RETRY OR FAIL OUTBOX RECORD
    # ========================================================

    @classmethod
    def mark_failed(
        cls,
        *,
        outbox_id: int,
        lock_token: uuid.UUID,
        error: Exception | str,
        retry_delay_seconds: int | None = None,
    ) -> bool:
        """
        Record a failed processing attempt.

        If attempts remain, the record returns to PENDING
        with a future available_at timestamp.

        Otherwise, it becomes permanently FAILED.

        Returns False if the worker no longer owns the record.
        """

        now = timezone.now()

        with transaction.atomic():
            record = (
                NotificationOutbox.objects
                .select_for_update()
                .filter(
                    pk=outbox_id,
                    status=NotificationOutbox.Status.PROCESSING,
                    lock_token=lock_token,
                )
                .first()
            )

            if record is None:
                return False

            record.last_error = str(error)[:cls.MAX_ERROR_LENGTH]

            record.locked_at = None
            record.locked_until = None
            record.lock_token = None

            if record.attempts >= record.max_attempts:
                record.status = NotificationOutbox.Status.FAILED

            else:
                if retry_delay_seconds is None:
                    retry_delay_seconds = (
                        cls._get_retry_delay(
                            attempts=record.attempts,
                        )
                    )

                if retry_delay_seconds < 0:
                    raise ValueError(
                        "retry_delay_seconds cannot be negative."
                    )

                record.status = NotificationOutbox.Status.PENDING

                record.available_at = now + timedelta(
                    seconds=retry_delay_seconds,
                )

            record.save(
                update_fields=[
                    "status",
                    "last_error",
                    "locked_at",
                    "locked_until",
                    "lock_token",
                    "available_at",
                    "updated_at",
                ]
            )

            return True

    # ========================================================
    # RETRY HELPERS
    # ========================================================

    @classmethod
    def _get_retry_delay(
        cls,
        *,
        attempts: int,
    ) -> int:
        """
        Calculate exponential retry delay.

        Example:
        Attempt 1: 30 seconds
        Attempt 2: 60 seconds
        Attempt 3: 120 seconds
        Attempt 4: 240 seconds

        The delay is capped at one hour.
        """

        exponent = max(attempts - 1, 0)

        delay = (
            cls.BASE_RETRY_DELAY_SECONDS
            * (2 ** exponent)
        )

        return min(
            delay,
            cls.MAX_RETRY_DELAY_SECONDS,
        )
