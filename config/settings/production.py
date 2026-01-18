"""
Production-specific Django settings.

This module extends base settings with production-specific configurations.
"""

import os

from .base import *  # noqa: F401, F403

DEBUG = False

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")

# Database - PostgreSQL for production
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
                "CONN_MAX_AGE": 60,
                "OPTIONS": {
                    "sslmode": "require",
                },
            }
        }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("DB_NAME"),
            "USER": os.getenv("DB_USER"),
            "PASSWORD": os.getenv("DB_PASSWORD"),
            "HOST": os.getenv("DB_HOST"),
            "PORT": os.getenv("DB_PORT", "5432"),
            "CONN_MAX_AGE": 60,
            "OPTIONS": {
                "sslmode": "require",
            },
        }
    }

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Static files
STATIC_ROOT = BASE_DIR / "staticfiles"  # noqa: F405

# Logging configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
    },
}
