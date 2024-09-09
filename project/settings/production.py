import dj_database_url
from decouple import config

from .base import *
from .base import BASE_DIR

API_URL = "https://kingdom-nurturing-suite.onrender.com/api"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

DATABASES["default"] = dj_database_url.parse(config("DATABASE_URL"))

EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
