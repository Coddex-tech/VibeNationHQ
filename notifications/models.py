from __future__ import annotations

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from django.utils import timezone


# ============================================================
# BASE MODEL
# ============================================================

class TimeStampedModel(models.Model):
    """
    Abstract base model providing creation and update timestamps.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# ============================================================
# NOTIFICATION
# ============================================================

class Notification(TimeStampedModel):
    """
    An item displayed in a user's notification centre.

    A notification can represent:
    - One individual event.
    - Multiple related events grouped together.

    NotificationEvent stores the individual underlying actions.
    """

    class Category(models.TextChoices):
        MENTIONS = "mentions", "Mentions"
        FOLLOWERS = "followers", "Followers"
        FOLLOWING = "following", "Following"
        ACTIVITY = "activity", "Activity"
        SYSTEM = "system", "System"

    class Type(models.TextChoices):
        # Followers
        NEW_FOLLOWER = "new_follower", "New follower"

        # Community posts
        COMMUNITY_POST_LIKE = (
            "community_post_like",
            "Community post like",
        )
        COMMUNITY_POST_COMMENT = (
            "community_post_comment",
            "Community post comment",
        )

        # Community comments
        COMMUNITY_COMMENT_LIKE = (
            "community_comment_like",
            "Community comment like",
        )
        COMMUNITY_COMMENT_REPLY = (
            "community_comment_reply",
            "Community comment reply",
        )

        # Editorial articles
        EDITORIAL_ARTICLE_LIKE = (
            "editorial_article_like",
            "Editorial article like",
        )
        EDITORIAL_ARTICLE_COMMENT = (
            "editorial_article_comment",
            "Editorial article comment",
        )

        # Editorial comments
        EDITORIAL_COMMENT_LIKE = (
            "editorial_comment_like",
            "Editorial comment like",
        )
        EDITORIAL_COMMENT_REPLY = (
            "editorial_comment_reply",
            "Editorial comment reply",
        )

        # Mentions
        COMMUNITY_POST_MENTION = (
            "community_post_mention",
            "Community post mention",
        )
        COMMUNITY_COMMENT_MENTION = (
            "community_comment_mention",
            "Community comment mention",
        )
        EDITORIAL_COMMENT_MENTION = (
            "editorial_comment_mention",
            "Editorial comment mention",
        )

        # Platform
        SYSTEM_ANNOUNCEMENT = (
            "system_announcement",
            "System announcement",
        )

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )

    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        db_index=True,
    )

    notification_type = models.CharField(
        max_length=50,
        choices=Type.choices,
        db_index=True,
    )

    # Identifies notifications belonging to the same group.
    # Individual notifications leave this field NULL.
    grouping_key = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    # Optional reference to the primary object associated
    # with this notification.
    target_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )

    target_object_id = models.CharField(
        max_length=64,
        null=True,
        blank=True,
    )

    target = GenericForeignKey(
        "target_content_type",
        "target_object_id",
    )

    # Flexible presentation and navigation information.
    metadata = models.JSONField(
        default=dict,
        blank=True,
    )

    # NULL means unread.
    # A timestamp means read.
    read_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    # Soft deletion from the recipient's notification centre.
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    # Number of currently active events represented by this item.
    event_count = models.PositiveIntegerField(default=0)

    # Time of the latest event contributing to this notification.
    latest_event_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
    )

    class Meta:
        ordering = ("-latest_event_at", "-pk")

        constraints = [
            models.UniqueConstraint(
                fields=("recipient", "grouping_key"),
                condition=Q(grouping_key__isnull=False),
                name="unique_notification_recipient_group",
            ),
        ]

        indexes = [
            models.Index(
                fields=("recipient", "-latest_event_at"),
                name="notif_rec_latest_idx",
            ),
            models.Index(
                fields=("recipient", "category", "-latest_event_at"),
                name="notif_rec_cat_latest_idx",
            ),
            models.Index(
                fields=("recipient", "read_at", "-latest_event_at"),
                name="notif_rec_read_latest_idx",
            ),
            models.Index(
                fields=("target_content_type", "target_object_id"),
                name="notif_target_idx",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"{self.notification_type} "
            f"for {self.recipient_id}"
        )

    @property
    def is_read(self) -> bool:
        return self.read_at is not None

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None


# ============================================================
# NOTIFICATION EVENT
# ============================================================

class NotificationEvent(TimeStampedModel):
    """
    Records one individual action contributing to a notification.

    Examples:
    - A user following another user.
    - A user liking a community post.
    - A user commenting on an editorial article.

    Event history is independent of the original like/follow
    record and can survive its deletion.
    """

    class Type(models.TextChoices):
        FOLLOW = "follow", "Follow"

        # Community posts
        COMMUNITY_POST_LIKE = (
            "community_post_like",
            "Community post like",
        )
        COMMUNITY_POST_COMMENT = (
            "community_post_comment",
            "Community post comment",
        )

        # Community comments
        COMMUNITY_COMMENT_LIKE = (
            "community_comment_like",
            "Community comment like",
        )
        COMMUNITY_COMMENT_REPLY = (
            "community_comment_reply",
            "Community comment reply",
        )

        # Editorial articles
        EDITORIAL_ARTICLE_LIKE = (
            "editorial_article_like",
            "Editorial article like",
        )
        EDITORIAL_ARTICLE_COMMENT = (
            "editorial_article_comment",
            "Editorial article comment",
        )

        # Editorial comments
        EDITORIAL_COMMENT_LIKE = (
            "editorial_comment_like",
            "Editorial comment like",
        )
        EDITORIAL_COMMENT_REPLY = (
            "editorial_comment_reply",
            "Editorial comment reply",
        )

        # Mentions
        COMMUNITY_POST_MENTION = (
            "community_post_mention",
            "Community post mention",
        )
        COMMUNITY_COMMENT_MENTION = (
            "community_comment_mention",
            "Community comment mention",
        )
        EDITORIAL_COMMENT_MENTION = (
            "editorial_comment_mention",
            "Editorial comment mention",
        )

        # Platform
        SYSTEM_ANNOUNCEMENT = (
            "system_announcement",
            "System announcement",
        )

    notification = models.ForeignKey(
        Notification,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
    )

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_events_received",
    )

    # Preserve event history if the actor's account is deleted.
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notification_events_performed",
    )

    event_type = models.CharField(
        max_length=50,
        choices=Type.choices,
        db_index=True,
    )

    # Generic reference to the object involved in the event.
    target_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )

    target_object_id = models.CharField(
        max_length=64,
        null=True,
        blank=True,
    )

    target = GenericForeignKey(
        "target_content_type",
        "target_object_id",
    )

    # Event-specific information, such as the exact comment ID.
    metadata = models.JSONField(
        default=dict,
        blank=True,
    )

    # Likes and follows can become inactive after unlike/unfollow.
    # Comments, replies and mentions normally remain active.
    is_active = models.BooleanField(
        default=True,
        db_index=True,
    )

    # Prevent duplicate events when an action is retried.
    idempotency_key = models.UUIDField(
        null=True,
        blank=True,
        unique=True,
    )

    class Meta:
        ordering = ("-created_at", "-pk")

        indexes = [
            models.Index(
                fields=("recipient", "-created_at"),
                name="notif_evt_rec_created_idx",
            ),
            models.Index(
                fields=("notification", "is_active"),
                name="notif_evt_notif_active_idx",
            ),
            models.Index(
                fields=("recipient", "event_type", "-created_at"),
                name="notif_evt_rec_type_idx",
            ),
            models.Index(
                fields=("actor", "event_type", "-created_at"),
                name="notif_evt_actor_type_idx",
            ),
            models.Index(
                fields=("target_content_type", "target_object_id"),
                name="notif_evt_target_idx",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"{self.event_type}: "
            f"{self.actor_id} -> {self.recipient_id}"
        )


# ============================================================
# NOTIFICATION PREFERENCES
# ============================================================

class NotificationPreference(TimeStampedModel):
    """
    Stores global notification settings for a user.

    Category-specific settings are stored separately in
    NotificationCategoryPreference.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_preferences",
    )

    # Global channel switches.
    in_app_enabled = models.BooleanField(default=True)
    push_enabled = models.BooleanField(default=True)

    # IANA timezone, e.g. Africa/Lagos.
    # Used for recipient-local daily follower grouping.
    timezone = models.CharField(
        max_length=64,
        default="Africa/Lagos",
    )

    def __str__(self) -> str:
        return f"Notification preferences for {self.user_id}"


# ============================================================
# NOTIFICATION CATEGORY PREFERENCES
# ============================================================

class NotificationCategoryPreference(TimeStampedModel):
    """
    Stores notification preferences for individual categories.

    Each user can independently enable or disable in-app
    and push notifications for each category.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_category_preferences",
    )

    category = models.CharField(
        max_length=20,
        choices=Notification.Category.choices,
    )

    in_app_enabled = models.BooleanField(default=True)
    push_enabled = models.BooleanField(default=True)

    class Meta:
        ordering = ("category",)

        constraints = [
            models.UniqueConstraint(
                fields=("user", "category"),
                name="unique_user_notification_category",
            ),
        ]

        indexes = [
            models.Index(
                fields=("user", "category"),
                name="notif_cat_pref_user_idx",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"{self.category} preferences "
            f"for {self.user_id}"
        )


# ============================================================
# PUSH SUBSCRIPTION
# ============================================================

class PushSubscription(TimeStampedModel):
    """
    Stores a browser/device Web Push subscription.

    A user may have multiple active subscriptions.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="push_subscriptions",
    )

    endpoint = models.TextField(unique=True)

    p256dh_key = models.TextField()
    auth_key = models.TextField()

    expiration_time = models.DateTimeField(
        null=True,
        blank=True,
    )

    user_agent = models.TextField(
        blank=True,
        default="",
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
    )

    last_used_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        indexes = [
            models.Index(
                fields=("user", "is_active"),
                name="push_sub_user_active_idx",
            ),
        ]

    def __str__(self) -> str:
        return f"Push subscription for {self.user_id}"


# ============================================================
# NOTIFICATION DELIVERY
# ============================================================

class NotificationDelivery(TimeStampedModel):
    """
    Tracks delivery attempts for individual notification events.

    This makes delivery status, retries and provider failures
    observable without changing the notification itself.
    """

    class Channel(models.TextChoices):
        PUSH = "push", "Push"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        SENT = "sent", "Sent"
        FAILED = "failed", "Failed"
        SKIPPED = "skipped", "Skipped"

    event = models.ForeignKey(
        NotificationEvent,
        on_delete=models.CASCADE,
        related_name="deliveries",
    )

    # Required because each delivery is tied to one subscription.
    subscription = models.ForeignKey(
        PushSubscription,
        on_delete=models.CASCADE,
        related_name="deliveries",
    )

    channel = models.CharField(
        max_length=20,
        choices=Channel.choices,
        default=Channel.PUSH,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )

    attempts = models.PositiveIntegerField(default=0)

    next_attempt_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
    )

    sent_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    last_error = models.TextField(
        blank=True,
        default="",
    )

    provider_response = models.JSONField(
        default=dict,
        blank=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("event", "subscription", "channel"),
                name="unique_event_subscription_channel",
            ),
        ]

        indexes = [
            models.Index(
                fields=("status", "next_attempt_at"),
                name="notif_delivery_retry_idx",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.channel}: {self.status}"


# ============================================================
# NOTIFICATION OUTBOX
# ============================================================

class NotificationOutbox(TimeStampedModel):
    """
    Reliable queue of background work to be dispatched to Celery.

    Outbox records are committed in the same database transaction
    as the business action and notification event.

    A separate worker can safely retry dispatching pending records.
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        PROCESSED = "processed", "Processed"
        FAILED = "failed", "Failed"

    task_type = models.CharField(
        max_length=100,
        db_index=True,
    )

    event = models.ForeignKey(
        NotificationEvent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="outbox_records",
    )

    payload = models.JSONField(
        default=dict,
        blank=True,
    )

    # Prevent duplicate background jobs.
    idempotency_key = models.CharField(
        max_length=255,
        unique=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )

    attempts = models.PositiveIntegerField(default=0)

    # Maximum processing attempts before terminal failure.
    max_attempts = models.PositiveIntegerField(default=8)

    available_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
    )

    # Worker lease information.
    # A worker can reclaim a record after this timestamp expires.
    locked_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    locked_until = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
    )

    lock_token = models.UUIDField(
        null=True,
        blank=True,
        editable=False,
    )

    processed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    last_error = models.TextField(
        blank=True,
        default="",
    )

    class Meta:
        ordering = ("available_at", "pk")

        indexes = [
            models.Index(
                fields=("status", "available_at"),
                name="notif_outbox_pending_idx",
            ),
            models.Index(
                fields=("status", "locked_until"),
                name="notif_outbox_lock_idx",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.task_type}: {self.status}"
