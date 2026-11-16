from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group, User
from django.contrib.sessions.models import Session
from django.db.migrations.recorder import MigrationRecorder
from django.shortcuts import redirect, render
from django.utils import timezone

from .forms import RegistrationForm


def register(request):
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")
    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.save())
        messages.success(request, "Your account has been created.")
        return redirect("accounts:dashboard")
    return render(request, "accounts/register.html", {"form": form})


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

