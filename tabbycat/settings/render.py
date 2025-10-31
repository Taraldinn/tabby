import logging
import os
import socket

import dj_database_url
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.redis import RedisIntegration

from .core import TABBYCAT_VERSION

# ==============================================================================
# IPv4 Fix for Render + Supabase
# ==============================================================================
# Render doesn't support outbound IPv6, but Supabase may resolve to IPv6 first.
# Force IPv4 resolution to ensure database connectivity.

old_getaddrinfo = socket.getaddrinfo


def new_getaddrinfo(host, *args, **kwargs):
    """Force IPv4 address resolution for all socket connections."""
    kwargs["family"] = socket.AF_INET
    return old_getaddrinfo(host, *args, **kwargs)


socket.getaddrinfo = new_getaddrinfo

# ==============================================================================
# Render per https://render.com/docs/deploy-django
# ==============================================================================

# Store Tab Director Emails for reporting purposes
if os.environ.get("TAB_DIRECTOR_EMAIL", ""):
    TAB_DIRECTOR_EMAIL = os.environ.get("TAB_DIRECTOR_EMAIL")

if os.environ.get("DJANGO_SECRET_KEY", ""):
    SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")

# https://docs.djangoproject.com/en/3.0/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ["*"]

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# ==============================================================================
# Postgres
# ==============================================================================

# Parse database configuration from $DATABASE_URL
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    # Parse database URL and enforce SSL for Supabase and other cloud providers
    db_config = dj_database_url.parse(DATABASE_URL, conn_max_age=600)

    # Ensure SSL is enabled for secure connections (required by Supabase)
    if "OPTIONS" not in db_config:
        db_config["OPTIONS"] = {}

    # Force SSL mode if not already specified in the URL
    if "sslmode" not in DATABASE_URL.lower():
        db_config["OPTIONS"]["sslmode"] = "require"

    DATABASES = {"default": db_config}
else:
    # Default database configuration for local development
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "tabbycat",
            "USER": "postgres",
            "PASSWORD": "postgres",
            "HOST": "localhost",
            "PORT": "5432",
        }
    }

# ==============================================================================
# Redis
# ==============================================================================

# Support both REDIS_URL and individual REDIS_HOST/REDIS_PORT
REDIS_URL = os.environ.get("REDIS_URL")
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = os.environ.get("REDIS_PORT", "6379")

if REDIS_URL:
    # Use REDIS_URL if available (preferred for Render)
    redis_location = REDIS_URL
else:
    # Fall back to host/port configuration
    redis_location = f"redis://{REDIS_HOST}:{REDIS_PORT}"

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": redis_location,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "SOCKET_CONNECT_TIMEOUT": 5,
            "SOCKET_TIMEOUT": 60,
            "IGNORE_EXCEPTIONS": True,  # Don't crash on say ConnectionError due to limits
        },
    },
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [redis_location],
        },
    },
}

# ==============================================================================
# Email Configuration
# ==============================================================================

# Email configuration from environment variables
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

EMAIL_HOST = os.environ.get("EMAIL_HOST", "localhost")

email_port = os.environ.get("EMAIL_PORT")
if email_port:
    EMAIL_PORT = int(email_port)

EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")

email_use_tls = os.environ.get("EMAIL_USE_TLS", "").lower()
EMAIL_USE_TLS = email_use_tls in ("true", "1", "yes")

# Default FROM email address
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER)
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# ==============================================================================
# Sentry
# ==============================================================================

if not os.environ.get("DISABLE_SENTRY"):
    DISABLE_SENTRY = False
    sentry_sdk.init(
        dsn="https://6bf2099f349542f4b9baf73ca9789597@o85113.ingest.sentry.io/185382",
        integrations=[
            DjangoIntegration(),
            LoggingIntegration(event_level=logging.WARNING),
            RedisIntegration(),
        ],
        send_default_pii=True,
        release=TABBYCAT_VERSION,
    )
