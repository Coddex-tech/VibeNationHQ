from django.contrib import admin, messages
from django.utils import timezone
from datetime import timedelta
import random

from .models import BackupCode


@admin.register(BackupCode)
class BackupCodeAdmin(admin.ModelAdmin):

    list_display = ("user", "code", "used", "expires_at")
    list_filter = ("used",)

    actions = ["generate_backup_code"]

    def generate_backup_code(self, request, queryset):

        for record in queryset:

            # 🔥 generate fresh code
            code = str(random.randint(100000, 999999))

            record.code = code
            record.used = False
            record.expires_at = timezone.now() + timedelta(minutes=15)
            record.save()

            self.message_user(
                request,
                f"Backup Code for {record.user.username}: {code} (valid 15 mins, one-time use)"
            )

    generate_backup_code.short_description = "Generate 15-min backup login code"