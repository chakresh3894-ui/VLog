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

## Validation

```powershell
python manage.py check
python manage.py test
```

Tests require the PostgreSQL values in `.env` because Django creates a temporary test database.
