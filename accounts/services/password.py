from django.db import transaction
from django.utils import timezone

from .sessions import UserSession


@transaction.atomic
def change_password(
    *,
    user,
    new_password,
    current_session_id,
):
    user.set_password(new_password)

    user.save(
        update_fields=[
            "password",
            "updated_at",
        ],
    )

    (
        UserSession.objects
        .filter(
            user=user,
            revoked_at__isnull=True,
        )
        .exclude(
            id=current_session_id,
        )
        .update(
            revoked_at=timezone.now(),
        )
    )

    return user