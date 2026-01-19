"""
Staging Django settings for local production simulation.

Inherits from production settings but disables SSL-specific configurations
that require real infrastructure (reverse proxy, cloud database with SSL).

Usage:
    docker-compose --env-file .env.staging up --build
"""

from .production import *  # noqa: F401, F403

# Disable SSL redirect (no reverse proxy locally)
SECURE_SSL_REDIRECT = False

# Disable secure cookies (no HTTPS locally)
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Disable HSTS (not relevant without HTTPS)
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# Database SSL - disabled for local Docker Postgres
# (Cloud databases like Render/Heroku have SSL enabled by default)
DATABASES["default"]["OPTIONS"]["sslmode"] = "disable"  # noqa: F405
