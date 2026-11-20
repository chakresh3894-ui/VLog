import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db import models
from django.utils import timezone


class PhoneVerification(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=16, unique=True)
    is_verified = models.BooleanField(default=False)
    otp_hash = models.CharField(max_length=128, blank=True)
    otp_expires_at = models.DateTimeField(null=True, blank=True)
    otp_attempts = models.PositiveSmallIntegerField(default=0)
    otp_last_sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def generate_otp(self):
        code = str(secrets.randbelow(9000) + 1000)
        self.otp_hash = make_password(code)
        self.otp_expires_at = timezone.now() + timedelta(minutes=5)
        self.otp_attempts = 0
        self.otp_last_sent_at = timezone.now()
        return code

