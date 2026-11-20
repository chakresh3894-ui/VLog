from django.contrib import admin

from .models import PhoneVerification


@admin.register(PhoneVerification)
class PhoneVerificationAdmin(admin.ModelAdmin):
    list_display = ("user", "phone_number", "is_verified", "otp_expires_at")
    search_fields = ("user__username", "phone_number")
    readonly_fields = ("otp_hash", "otp_expires_at", "otp_attempts", "otp_last_sent_at")

