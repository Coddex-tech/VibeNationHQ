from django.db.models import F, Prefetch, Window
from django.db.models.functions import RowNumber

from rest_framework import generics
from rest_framework.pagination import CursorPagination
from rest_framework.permissions import IsAuthenticated

from accounts.authentications import VibeNationSessionAuthentication
from notifications.models import Notification, NotificationEvent
from notifications.serializers.notification import NotificationSerializer


class NotificationCursorPagination(CursorPagination):
    page_size = 20
    ordering = ("-latest_event_at", "-pk")


class NotificationListView(generics.ListAPIView):
    """
    Returns the authenticated user's notification centre.

    Notifications are loaded using cursor pagination.
    Each notification includes at most three latest active actors.
    """

    authentication_classes = [
        VibeNationSessionAuthentication,
    ]
    permission_classes = [
        IsAuthenticated,
    ]

    serializer_class = NotificationSerializer
    pagination_class = NotificationCursorPagination

    def get_queryset(self):
        latest_active_events = (
            NotificationEvent.objects
            .filter(
                is_active=True,
                actor__isnull=False,
            )
            .annotate(
                event_rank=Window(
                    expression=RowNumber(),
                    partition_by=[
                        F("notification_id"),
                    ],
                    order_by=[
                        F("created_at").desc(),
                        F("pk").desc(),
                    ],
                )
            )
            .filter(event_rank__lte=3)
            .select_related("actor")
            .order_by(
                "notification_id",
                "-created_at",
                "-pk",
            )
        )

        return (
            Notification.objects
            .filter(
                recipient=self.request.user,
                deleted_at__isnull=True,
            )
            .select_related(
                "target_content_type",
            )
            .prefetch_related(
                Prefetch(
                    "events",
                    queryset=latest_active_events,
                    to_attr="latest_active_events",
                )
            )
            .order_by(
                "-latest_event_at",
                "-pk",
            )
        )