# Django Authentication Portal

Everything for this application is contained in this folder.

## Setup

1. Install Python 3.11+ and PostgreSQL.
2. Create a PostgreSQL database and user.
3. In this folder, run:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   Copy-Item .env.example .env
   ```

4. Edit `.env` with your PostgreSQL credentials and a unique Django secret key.
5. Apply built-in Django migrations and start the app:

   ```powershell
   python manage.py migrate
   python manage.py runserver
   ```

Visit `http://127.0.0.1:8000/register/` to create an account. The application uses Django's built-in user model and password hashers; no custom model or migration is needed.

## Phone verification and password recovery

- New registrations require an international-format phone number and a 4-digit verification code.
- The OTP is stored as a hash, expires after 5 minutes, permits 5 attempts, and can be resent after 60 seconds.
- While `DJANGO_DEBUG=True`, the OTP is printed in the development-server terminal and shown on the verification page. Never enable this display in production.
- The **Forgot your password?** link uses Django's password-reset flow. With the default console email backend, the reset link is printed in the development-server terminal. Configure a real SMTP email backend before production.

### Sending real email with Gmail

Django includes SMTP email support, so no additional Python package is required. To send reset emails through a personal Gmail account:

1. Turn on 2-Step Verification for the Gmail account.
2. Create a 16-digit Google App Password for this application.
3. In `.env`, set `DJANGO_EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend`, then fill in `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, and `DEFAULT_FROM_EMAIL` with the values shown in `.env.example`.
4. Restart `python manage.py runserver` and use the password-reset page to test delivery.

Never commit `.env` or share the app password. Gmail App Passwords require 2-Step Verification and can be revoked from your Google Account.

After pulling these changes, apply the new database migration:

```powershell
python manage.py migrate
```

## Validation

```powershell
python manage.py check
python manage.py test
```

Tests require the PostgreSQL values in `.env` because Django creates a temporary test database.
