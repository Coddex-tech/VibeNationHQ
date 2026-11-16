
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from notifications.models import NotificationOutbox
from notifications.services.outbox import NotificationOutboxService


class NotificationOutboxServiceTestCase(TestCase):

    def create_outbox(self, **kwargs):
        defaults = {
            "task_type": "notification.dispatch_push",
            "idempotency_key": "test-outbox-event-1",
            "payload": {"event_id": 100},
        }
        defaults.update(kwargs)

        return NotificationOutbox.objects.create(**defaults)

    def test_claim_pending_outbox_record(self):
        outbox = self.create_outbox()

        claimed = NotificationOutboxService.claim_pending()

        self.assertEqual(len(claimed), 1)
        self.assertEqual(claimed[0].pk, outbox.pk)

        outbox.refresh_from_db()

        self.assertEqual(
            outbox.status,
            NotificationOutbox.Status.PROCESSING,
        )
        self.assertEqual(outbox.attempts, 1)
        self.assertIsNotNone(outbox.lock_token)
        self.assertIsNotNone(outbox.locked_until)

    def test_future_outbox_record_is_not_claimed(self):
        outbox = self.create_outbox(
            available_at=timezone.now() + timedelta(hours=1),
        )

        claimed = NotificationOutboxService.claim_pending()

        self.assertEqual(claimed, [])

        outbox.refresh_from_db()

        self.assertEqual(
            outbox.status,
            NotificationOutbox.Status.PENDING,
        )

    def test_processed_record_cannot_be_claimed_again(self):
        self.create_outbox()

        claimed = NotificationOutboxService.claim_pending()
        record = claimed[0]

        result = NotificationOutboxService.mark_processed(
            outbox_id=record.pk,
            lock_token=record.lock_token,
        )

        self.assertTrue(result)

        record.refresh_from_db()

        self.assertEqual(
            record.status,
            NotificationOutbox.Status.PROCESSED,
        )
        self.assertIsNotNone(record.processed_at)
        self.assertIsNone(record.lock_token)

        self.assertEqual(
            NotificationOutboxService.claim_pending(),
            [],
        )

    def test_failed_record_is_scheduled_for_retry(self):
        self.create_outbox()

        claimed = NotificationOutboxService.claim_pending()
        record = claimed[0]

        result = NotificationOutboxService.mark_failed(
            outbox_id=record.pk,
            lock_token=record.lock_token,
            error="Temporary provider failure",
            retry_delay_seconds=60,
        )

        self.assertTrue(result)

        record.refresh_from_db()

        self.assertEqual(
            record.status,
            NotificationOutbox.Status.PENDING,
        )
        self.assertEqual(
            record.last_error,
            "Temporary provider failure",
        )
        self.assertIsNone(record.lock_token)

        self.assertGreater(
            record.available_at,
            timezone.now(),
        )

    def test_expired_processing_lease_can_be_reclaimed(self):
        self.create_outbox()

        first_claim = NotificationOutboxService.claim_pending()
        first_record = first_claim[0]
        first_token = first_record.lock_token

        NotificationOutbox.objects.filter(
            pk=first_record.pk,
        ).update(
            locked_until=timezone.now() - timedelta(seconds=1),
        )

        second_claim = NotificationOutboxService.claim_pending()
        second_record = second_claim[0]

        self.assertEqual(
            first_record.pk,
            second_record.pk,
        )
        self.assertNotEqual(
            first_token,
            second_record.lock_token,
        )
        self.assertEqual(second_record.attempts, 2)

    def test_old_worker_cannot_complete_reclaimed_record(self):
        self.create_outbox()

        first_claim = NotificationOutboxService.claim_pending()
        first_record = first_claim[0]
        first_token = first_record.lock_token

        NotificationOutbox.objects.filter(
            pk=first_record.pk,
        ).update(
            locked_until=timezone.now() - timedelta(seconds=1),
        )

        second_claim = NotificationOutboxService.claim_pending()
        second_record = second_claim[0]

        result = NotificationOutboxService.mark_processed(
            outbox_id=second_record.pk,
            lock_token=first_token,
        )

        self.assertFalse(result)

        second_record.refresh_from_db()

        self.assertEqual(
            second_record.status,
            NotificationOutbox.Status.PROCESSING,
        )

    def test_maximum_attempts_marks_record_failed(self):
        outbox = self.create_outbox(
            attempts=7,
            max_attempts=8,
        )

        claimed = NotificationOutboxService.claim_pending()
        record = claimed[0]

        self.assertEqual(record.attempts, 8)

        result = NotificationOutboxService.mark_failed(
            outbox_id=record.pk,
            lock_token=record.lock_token,
            error="Final processing failure",
        )

        self.assertTrue(result)

        outbox.refresh_from_db()

        self.assertEqual(
            outbox.status,
            NotificationOutbox.Status.FAILED,
        )
        self.assertEqual(outbox.attempts, 8)
        self.assertIsNone(outbox.lock_token)

    def test_exhausted_pending_record_is_marked_failed(self):
        outbox = self.create_outbox(
            attempts=8,
            max_attempts=8,
        )

        claimed = NotificationOutboxService.claim_pending()

        self.assertEqual(claimed, [])

        outbox.refresh_from_db()

        self.assertEqual(
            outbox.status,
            NotificationOutbox.Status.FAILED,
        )

    def test_invalid_lock_token_cannot_complete_record(self):
        self.create_outbox()

        claimed = NotificationOutboxService.claim_pending()
        record = claimed[0]

        result = NotificationOutboxService.mark_processed(
            outbox_id=record.pk,
            lock_token=__import__("uuid").uuid4(),
        )

        self.assertFalse(result)

        record.refresh_from_db()

        self.assertEqual(
            record.status,
            NotificationOutbox.Status.PROCESSING,
        )

    def test_retry_delay_uses_exponential_backoff(self):
        self.assertEqual(
            NotificationOutboxService._get_retry_delay(attempts=1),
            30,
        )
        self.assertEqual(
            NotificationOutboxService._get_retry_delay(attempts=2),
            60,
        )
        self.assertEqual(
            NotificationOutboxService._get_retry_delay(attempts=3),
            120,
        )
        self.assertEqual(
            NotificationOutboxService._get_retry_delay(attempts=4),
            240,
        )
        self.assertEqual(
            NotificationOutboxService._get_retry_delay(attempts=20),
            3600,
        )
