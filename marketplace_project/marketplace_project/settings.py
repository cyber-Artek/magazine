"""
Django settings for marketplace_project project.
"""

from pathlib import Path
from django.utils.translation import gettext_lazy as _
from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("SECRET_KEY")
DEBUG = True
ALLOWED_HOSTS: list[str] = []

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "users",
    "orders",
    "products",
    "reviews",
    "home",

]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "marketplace_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "marketplace_project.wsgi.application"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        )
    },
    {"NAME": ("django.contrib.auth.password_validation."
              "MinimumLengthValidator")},

    {"NAME": ("django.contrib.auth.password_validation."
              "CommonPasswordValidator")},

    {"NAME": ("django.contrib.auth.password_validation."
              "NumericPasswordValidator")},
]

LANGUAGE_CODE = "en"
LANGUAGES = [
    ("uk", _("Ukrainian")),
    ("en", _("English")),
    ("es", _("Español")),
]
LOCALE_PATHS = [
    BASE_DIR / "locale",
]

TIME_ZONE = "Europe/Kiev"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "users.CustomUser"

LOGIN_URL = "login"
LOGOUT_REDIRECT_URL = "login"
LOGIN_REDIRECT_URL = "product-list"

# ===== Налаштування email (приклад для Gmail) =====
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")  # твій email
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")  # пароль або app password
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Куди надсилати нотифікації про замовлення
ORDER_NOTIFICATION_EMAIL = os.environ.get("ORDER_NOTIFICATION_EMAIL", EMAIL_HOST_USER)
