from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import PhoneVerification


class AccountFlowTests(TestCase):
    def test_registration_requires_phone_verification(self):
        response = self.client.post(reverse("accounts:register"), {
            "username": "newuser", "email": "newuser@example.com",
            "phone_number": "+919876543210",
            "password1": "StrongPassword!123", "password2": "StrongPassword!123",
        })
        self.assertRedirects(response, reverse("accounts:verify_phone"))
        user = User.objects.get(username="newuser")
        self.assertFalse(user.is_active)
        self.assertFalse(PhoneVerification.objects.get(user=user).is_verified)

    def test_correct_otp_activates_account(self):
        user = User.objects.create_user(username="newuser", password="StrongPassword!123", is_active=False)
        verification = PhoneVerification.objects.create(user=user, phone_number="+919876543210")
        code = verification.generate_otp()
        verification.save()
        session = self.client.session
        session["pending_verification_user_id"] = user.id
        session.save()

        response = self.client.post(reverse("accounts:verify_phone"), {"otp": code})

        self.assertRedirects(response, reverse("accounts:dashboard"))
        user.refresh_from_db()
        verification.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertTrue(verification.is_verified)

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("accounts:dashboard"))
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={reverse('accounts:dashboard')}")

    def test_page_two_requires_login(self):
        response = self.client.get(reverse("accounts:page_two"))
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={reverse('accounts:page_two')}")

    def test_admin_overview_requires_superuser(self):
        user = User.objects.create_user(username="member", password="StrongPassword!123")
        self.client.force_login(user)
        response = self.client.get(reverse("accounts:admin_overview"))
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={reverse('accounts:admin_overview')}")

    def test_superuser_can_view_admin_overview(self):
        user = User.objects.create_superuser(username="admin", password="StrongPassword!123")
        self.client.force_login(user)
        response = self.client.get(reverse("accounts:admin_overview"))
        self.assertContains(response, "Admin overview")

    def test_password_reset_page_is_available(self):
        response = self.client.get(reverse("accounts:password_reset"))
        self.assertContains(response, "Reset your password")

