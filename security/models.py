from django.db import models
from django.contrib.auth.models import User
from django_otp.plugins.otp_static.models import StaticDevice
from django.utils import timezone

class BackupCode(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    device = models.ForeignKey(StaticDevice, on_delete=models.CASCADE)

    code = models.CharField(max_length=10, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    used = models.BooleanField(default=False)

    def is_valid(self):
        if self.used:
            return False
        return timezone.now() <= self.expires_at

    def mark_used(self):
        self.used = True
        self.save(update_fields=["used"])