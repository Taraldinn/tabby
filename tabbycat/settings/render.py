import logging
import os

import dj_database_url
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.redis import RedisIntegration

from .core import TABBYCAT_VERSION

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
DATABASES = {
    "default": dj_database_url.config(
        # Feel free to alter this value to suit your needs.
        default="postgresql://postgres:postgres@localhost:5432/mysite",
        conn_max_age=600,
    )
}

# ==============================================================================
# Redis
# ==============================================================================

# Support both REDIS_URL and individual REDIS_HOST/REDIS_PORT
REDIS_URL = os.environ.get("REDIS_URL")
REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PORT = os.environ.get("REDIS_PORT")

if REDIS_URL:
    # Use REDIS_URL if available (preferred for Render)
    redis_location = REDIS_URL
else:
    # Fall back to host/port configuration
    redis_location = "redis://" + REDIS_HOST + ":" + REDIS_PORT

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
