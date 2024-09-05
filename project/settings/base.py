import os
from pathlib import Path

from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent

ENV = config("ENV")

SECRET_KEY = config("SECRET_KEY")
DEBUG = True if ENV == "development" else False
ALLOWED_HOSTS = config("HOSTS_ALLOWED").split(" ")

# Application definition

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "admin_honeypot",
    "django_use_email_as_username.apps.DjangoUseEmailAsUsernameConfig",
    "kns.custom_user.apps.CustomUserConfig",
    "cloudinary",
    "formtools",
    "django_countries",
    "tinymce",
]

LOCAL_APPS = [
    "kns.accounts",
    "kns.core",
    "kns.profiles",
    "kns.groups",
    "kns.skills",
    "kns.faith_milestones",
    "kns.vocations",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

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

ROOT_URLCONF = "project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "kns", "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "kns.core.context_processors.settings_context",
                "kns.profiles.context_processors.profile_context",
                "kns.groups.context_processors.group_context",
            ],
        },
    },
]

WSGI_APPLICATION = "project.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",
#     }
# }

# DATABASES["default"] = dj_database_url.parse(config("DATABASE_URL"))


# AUTH SETTINGS

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

AUTH_USER_MODEL = "custom_user.User"

LOGIN_URL = "accounts:login"
PASSWORD_RESET_COMPLETE_URL = "/accounts/login"

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/


STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "kns" / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# EMAIL CONFIG
ACCOUNT_EMAIL_SUBJECT_PREFIX = ""
DEFAULT_FROM_EMAIL = "Kingdom Nurturing Suite"

EMAIL_HOST = config("EMAIL_HOST")
EMAIL_PORT = config("EMAIL_PORT")
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")

# Cloudinary configuration

# flake8: noqa
# isort: off
import cloudinary
import cloudinary.api
import cloudinary.uploader

# isort: on

cloudinary.config(
    cloud_name=config(
        "CLOUDINARY_CLOUD_NAME",
        default="default_cloud_name",
    ),
    api_key=config(
        "CLOUDINARY_CLOUD_API_KEY",
        default="default_api_key",
    ),
    api_secret=config(
        "CLOUDINARY_CLOUD_API_SECRET",
        default="default_api_secret",
    ),
)
