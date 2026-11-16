from django.contrib.auth import get_user_model
from django.db.models import (
    Case,
    IntegerField,
    Max,
    Q,
    Value,
    When,
)
from django.db.models.functions import Lower

from rest_framework import generics
from rest_framework.response import Response

from accounts.api.permissions import IsOrdinaryVibeNationUser
from music.models import UserFollow, UserMention
from music.serializers.mention_suggestions import (
    MentionSuggestionSerializer,
)


User = get_user_model()


class MentionSuggestionsAPIView(generics.GenericAPIView):
    """
    Returns lightweight user suggestions for mention autocomplete.

    Empty query:
        Returns the five most recently mentioned distinct users.

    Non-empty query:
        Searches the current user's followers and following
        by username or display-name prefix.
    """

    serializer_class = MentionSuggestionSerializer
    permission_classes = [IsOrdinaryVibeNationUser]

    MAX_QUERY_LENGTH = 100
    MAX_RESULTS = 5

    def get_recent_suggestions(self, user):
        """
        Return up to five distinct users mentioned most recently.
        """

        recent_user_ids = list(
            UserMention.objects
            .filter(
                mentioner=user,
                mentioned_user__is_active=True,
                mentioned_user__is_staff=False,
            )
            .values("mentioned_user_id")
            .annotate(
                last_mentioned_at=Max("created_at"),
            )
            .order_by("-last_mentioned_at")
            .values_list("mentioned_user_id", flat=True)[
                :self.MAX_RESULTS
            ]
        )

        if not recent_user_ids:
            return User.objects.none()

        ordering = Case(
            *[
                When(pk=user_id, then=position)
                for position, user_id in enumerate(recent_user_ids)
            ],
            output_field=IntegerField(),
        )

        return (
            User.objects
            .filter(
                pk__in=recent_user_ids,
                is_active=True,
                is_staff=False,
            )
            .order_by(ordering)
        )

    def get_network_suggestions(self, user, query):
        """
        Search users in the current user's follower/following
        network using case-insensitive prefix matching.
        """

        following_ids = (
            UserFollow.objects
            .filter(follower=user)
            .values("following_id")
        )

        follower_ids = (
            UserFollow.objects
            .filter(following=user)
            .values("follower_id")
        )

        normalized_query = query.lower()

        return (
            User.objects
            .annotate(
                normalized_username=Lower("username"),
                normalized_display_name=Lower("display_name"),
            )
            .filter(
                Q(pk__in=following_ids)
                | Q(pk__in=follower_ids),
                is_active=True,
                is_staff=False,
            )
            .filter(
                Q(
                    normalized_username__startswith=normalized_query,
                )
                | Q(
                    normalized_display_name__startswith=normalized_query,
                )
            )
            .annotate(
                match_priority=Case(
                    When(
                        normalized_username__startswith=normalized_query,
                        then=Value(0),
                    ),
                    default=Value(1),
                    output_field=IntegerField(),
                ),
            )
            .order_by(
                "match_priority",
                "normalized_username",
            )[:self.MAX_RESULTS]
        )

    def get(self, request, *args, **kwargs):
        query = request.query_params.get("q", "").strip()

        if query.startswith("@"):
            query = query[1:]

        if len(query) > self.MAX_QUERY_LENGTH:
            query = query[:self.MAX_QUERY_LENGTH]

        if not query:
            suggestions = self.get_recent_suggestions(
                request.user,
            )
        else:
            suggestions = self.get_network_suggestions(
                request.user,
                query,
            )

        serializer = self.get_serializer(
            suggestions,
            many=True,
        )

        return Response({
            "results": serializer.data,
        })
