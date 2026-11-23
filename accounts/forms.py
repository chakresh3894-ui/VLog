from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.RegexField(
        regex=r"^\+?[1-9]\d{7,14}$",
        help_text="Use an international-format phone number, for example +919876543210.",
        error_messages={"invalid": "Enter a valid phone number."},
    )

    class Meta:
        model = User
        fields = ("username", "email", "phone_number", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].help_text = (
            "Your password must contain at least 8 characters, including uppercase "
            "and lowercase letters, a number, and a special character."
        )

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data["phone_number"]
        from .models import PhoneVerification
        if PhoneVerification.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError("An account with this phone number already exists.")
        return phone_number


class OTPVerificationForm(forms.Form):
    otp = forms.RegexField(
        regex=r"^\d{4}$",
        max_length=4,
        error_messages={"invalid": "Enter the 4-digit code."},
    )

