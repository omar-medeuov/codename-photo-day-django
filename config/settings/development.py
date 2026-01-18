"""
Development-specific Django settings.

This module extends base settings with development-specific configurations.
"""

import os

from .base import *  # noqa: F401, F403

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

# Database
# Use SQLite for development by default
USE_SQLITE = os.getenv("USE_SQLITE", "True").lower() in ("true", "1", "yes")

if USE_SQLITE:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
        }
    }
else:
    # PostgreSQL configuration for development
    DATABASE_URL = os.getenv("DATABASE_URL", "")
    if DATABASE_URL:
        import re

        match = re.match(
            r"postgres://(?P<user>[^:]+):(?P<password>[^@]+)@"
            r"(?P<host>[^:]+):(?P<port>\d+)/(?P<name>.+)",
            DATABASE_URL,
        )
        if match:
            DATABASES = {
                "default": {
                    "ENGINE": "django.db.backends.postgresql",
                    "NAME": match.group("name"),
                    "USER": match.group("user"),
                    "PASSWORD": match.group("password"),
                    "HOST": match.group("host"),
                    "PORT": match.group("port"),
                }
            }
    else:
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": os.getenv("DB_NAME", "todo_db"),
                "USER": os.getenv("DB_USER", "postgres"),
                "PASSWORD": os.getenv("DB_PASSWORD", "postgres"),
                "HOST": os.getenv("DB_HOST", "localhost"),
                "PORT": os.getenv("DB_PORT", "5432"),
            }
        }

# Email backend for development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# CORS settings for development (if needed)
CORS_ALLOW_ALL_ORIGINS = True
