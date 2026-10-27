import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure-CHANGE-THIS-BEFORE-DEPLOYMENT-qrtap-demo")
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = ["*"]
CSRF_TRUSTED_ORIGINS = ["https://*.vercel.app"]
INSTALLED_APPS = [
    "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
    "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
    "core",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "qrtap.urls"
TEMPLATES = [{"BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"], "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.debug",
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages"]}}]
WSGI_APPLICATION = "qrtap.wsgi.application"
# Database — this is the Blocker 1 fix.
# Vercel serverless functions each have their own /tmp, so SQLite on /tmp
# is NOT shared: every instance re-seeds its own database, table tokens
# rotate, orders vanish, and login sessions die when routing switches
# instances. The fix is one shared database outside Vercel: hosted Postgres.
# Set DATABASE_URL (or, via Vercel's Neon integration, POSTGRES_URL) and
# every instance talks to the SAME database, so data, tokens and sessions
# persist. Without a URL, Vercel falls back to /tmp SQLite (view-only mode)
# and local runs still use a local SQLite file.
_DB_URL = os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_URL")
if _DB_URL:
    import dj_database_url
    # conn_max_age=0: do not hold pooled connections across serverless
    # invocations (Neon's pooler manages the actual pooling).
    # SSL only for Postgres (Neon requires it); sqlite URLs must not get
    # an sslmode parameter or they crash with "sslmode is an invalid
    # keyword argument".
    _is_pg = _DB_URL.startswith(("postgres://", "postgresql://"))
    DATABASES = {"default": dj_database_url.parse(_DB_URL, conn_max_age=0, ssl_require=_is_pg)}
elif os.environ.get("VERCEL"):
    DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": "/tmp/db.sqlite3"}}
else:
    DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}
AUTH_PASSWORD_VALIDATORS = []
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {"staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"}}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/dashboard/"
LOGOUT_REDIRECT_URL = "/"
GST_RATE = 0.05
