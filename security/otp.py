from django.utils import timezone
from .models import BackupCode


def verify_backup_code(user, code):

    try:
        record = BackupCode.objects.get(
            user=user,
            code=code,
            used=False
        )
    except BackupCode.DoesNotExist:
        return False

    if timezone.now() > record.expires_at:
        return False

    # mark as used immediately
    record.used = True
    record.save(update_fields=["used"])

    return True