from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import Group, User
from django.contrib.sessions.models import Session
from django.db.migrations.recorder import MigrationRecorder
from django.shortcuts import redirect, render
from django.utils import timezone
from django.conf import settings

from .forms import OTPVerificationForm, RegistrationForm
from .models import PhoneVerification


OTP_MAX_ATTEMPTS = 5
OTP_RESEND_COOLDOWN_SECONDS = 60


def send_development_otp(request, verification):
    code = verification.generate_otp()
    verification.save()
    request.session["development_otp"] = code
    print(f"Development OTP for {verification.user.username}: {code}")


def register(request):
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")
    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        verification = PhoneVerification.objects.create(
            user=user,
            phone_number=form.cleaned_data["phone_number"],
        )
        send_development_otp(request, verification)
        request.session["pending_verification_user_id"] = user.id
        messages.success(request, "We generated a verification code for your phone number.")
        return redirect("accounts:verify_phone")
    return render(request, "accounts/register.html", {"form": form})


def verify_phone(request):
    user_id = request.session.get("pending_verification_user_id")
    verification = PhoneVerification.objects.filter(user_id=user_id, is_verified=False).select_related("user").first()
    if verification is None:
        messages.error(request, "Start registration before verifying a phone number.")
        return redirect("accounts:register")

    form = OTPVerificationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        if verification.otp_expires_at is None or verification.otp_expires_at <= timezone.now():
            messages.error(request, "This code has expired. Request a new code and try again.")
        elif verification.otp_attempts >= OTP_MAX_ATTEMPTS:
            messages.error(request, "You have used all five attempts. Request a new code.")
        else:
            verification.otp_attempts += 1
            if check_password(form.cleaned_data["otp"], verification.otp_hash):
                verification.is_verified = True
                verification.otp_hash = ""
                verification.otp_expires_at = None
                verification.otp_attempts = 0
                verification.save()
                verification.user.is_active = True
                verification.user.save(update_fields=["is_active"])
                request.session.pop("pending_verification_user_id", None)
                request.session.pop("development_otp", None)
                login(request, verification.user)
                messages.success(request, "Phone number verified. Your account is ready.")
                return redirect("accounts:dashboard")
            verification.save(update_fields=["otp_attempts", "updated_at"])
            messages.error(request, "That code is incorrect.")

    remaining_seconds = 0
    if verification.otp_last_sent_at:
        elapsed = (timezone.now() - verification.otp_last_sent_at).total_seconds()
        remaining_seconds = max(0, OTP_RESEND_COOLDOWN_SECONDS - int(elapsed))
    return render(request, "accounts/verify_phone.html", {
        "form": form,
        "phone_number": verification.phone_number,
        "development_otp": request.session.get("development_otp") if settings.DEBUG else None,
        "remaining_seconds": remaining_seconds,
    })


def resend_otp(request):
    if request.method != "POST":
        return redirect("accounts:verify_phone")
    user_id = request.session.get("pending_verification_user_id")
    verification = PhoneVerification.objects.filter(user_id=user_id, is_verified=False).select_related("user").first()
    if verification is None:
        return redirect("accounts:register")
    elapsed = (timezone.now() - verification.otp_last_sent_at).total_seconds() if verification.otp_last_sent_at else OTP_RESEND_COOLDOWN_SECONDS
    if elapsed < OTP_RESEND_COOLDOWN_SECONDS:
        messages.error(request, f"Wait {OTP_RESEND_COOLDOWN_SECONDS - int(elapsed)} seconds before requesting another code.")
    else:
        send_development_otp(request, verification)
        messages.success(request, "A new verification code has been generated.")
    return redirect("accounts:verify_phone")


@login_required
def dashboard(request):
    return render(request, "accounts/dashboard.html")


@login_required
def page_two(request):
    return render(request, "accounts/page_two.html")


@user_passes_test(lambda user: user.is_authenticated and user.is_superuser)
def admin_overview(request):
    context = {
        "user_count": User.objects.count(),
        "active_user_count": User.objects.filter(is_active=True).count(),
        "group_count": Group.objects.count(),
        "session_count": Session.objects.filter(expire_date__gt=timezone.now()).count(),
        "migration_count": MigrationRecorder.Migration.objects.count(),
        "users": User.objects.order_by("-date_joined")[:10],
    }
    return render(request, "accounts/admin_overview.html", context)

