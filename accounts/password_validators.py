import re
from difflib import SequenceMatcher

from django.core.exceptions import ValidationError


class StrongPasswordValidator:
    """Require a strong password that is not similar to the username."""

    def validate(self, password, user=None):
        username = getattr(user, "username", "") if user else ""
        username = username.strip().lower()

        if username:
            password_normalized = re.sub(r"[^a-z0-9]", "", password.lower())
            username_normalized = re.sub(r"[^a-z0-9]", "", username)

            is_similar = (
                username_normalized
                and (
                    password_normalized == username_normalized
                    or SequenceMatcher(None, password_normalized, username_normalized).ratio() >= 0.7
                )
            )
            if is_similar:
                raise ValidationError(
                    "Your password must not be similar to your username.",
                    code="password_too_similar",
                )

        strong_password = (
            len(password) >= 8
            and re.search(r"[A-Z]", password)
            and re.search(r"[a-z]", password)
            and re.search(r"\d", password)
            and re.search(r"[^A-Za-z0-9\s]", password)
        )

        if not strong_password:
            raise ValidationError(
                "Your password must contain at least 8 characters, including uppercase "
                "and lowercase letters, a number, and a special character.",
                code="password_too_weak",
            )

    def get_help_text(self):
        return (
            "Your password must contain at least 8 characters, including uppercase "
            "and lowercase letters, a number, and a special character."
        )
