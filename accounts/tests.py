from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class AccountFlowTests(TestCase):
    def test_registration_creates_logged_in_user(self):
        response = self.client.post(reverse("accounts:register"), {
            "username": "newuser", "email": "newuser@example.com",
            "password1": "StrongPassword!123", "password2": "StrongPassword!123",
        })
        self.assertRedirects(response, reverse("accounts:dashboard"))
        self.assertTrue(User.objects.filter(username="newuser").exists())

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

