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

# Save the original getaddrinfo before patching
_original_getaddrinfo = socket.getaddrinfo


def new_getaddrinfo(host, *args, **kwargs):
    """Force IPv4 address resolution for all socket connections."""
    # Force IPv4 family
    return _original_getaddrinfo(host, *args, family=socket.AF_INET, **kwargs)


# Apply the patch
socket.getaddrinfo = new_getaddrinfo


def resolve_hostname_to_ipv4(url):
    """
    Resolve hostname in DATABASE_URL to IPv4 address to bypass IPv6 issues.
    This is needed because Render doesn't support outbound IPv6 connections.
    """
    if not url or "supabase.co" not in url:
        return url

    import re

    # Extract hostname from postgresql://user:pass@HOSTNAME:port/db
    match = re.search(r"@([^:]+):(\d+)", url)
    if match:
        hostname = match.group(1)
        port = match.group(2)

        try:
            # Force IPv4 resolution using the original getaddrinfo with AF_INET
            addr_info = _original_getaddrinfo(
                hostname, 
                None, 
                socket.AF_INET,  # Force IPv4
                socket.SOCK_STREAM
            )
            if addr_info:
                ipv4_address = addr_info[0][4][0]  # Get the first IPv4 address
                # Replace hostname with IPv4 address
                new_url = url.replace(f"@{hostname}:", f"@{ipv4_address}:")
                print(f"🔧 IPv4 Fix: Resolved {hostname} → {ipv4_address}")
                return new_url
        except (socket.gaierror, IndexError) as e:
            print(f"⚠️  Could not resolve {hostname} to IPv4: {e}")
            print(f"   Will try with hostname anyway...")
            return url

    return url


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
DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()

# Resolve Supabase hostname to IPv4 to avoid Render's IPv6 connectivity issues
if DATABASE_URL and os.environ.get("ON_RENDER"):
    DATABASE_URL = resolve_hostname_to_ipv4(DATABASE_URL)

# Debug: Print DATABASE_URL status (password will be hidden in logs)
if os.environ.get("ON_RENDER"):
    if DATABASE_URL:
        # Show beginning and end of URL to help diagnose issues
        if len(DATABASE_URL) > 30:
            masked = DATABASE_URL[:15] + "..." + DATABASE_URL[-15:]
        else:
            masked = DATABASE_URL[:10] + "..."
        print(f"✓ DATABASE_URL is set (length: {len(DATABASE_URL)} chars)")
        print(f"  Preview: {masked}")
        print(
            f"  Starts with 'postgresql://': {DATABASE_URL.startswith('postgresql://')}"
        )
    else:
        print("✗ DATABASE_URL is NOT set or is empty!")
        print(f"  Raw value: '{os.environ.get('DATABASE_URL', 'NOT_FOUND')}'")

if (
    DATABASE_URL and len(DATABASE_URL) > 10
):  # Ensure it's not just whitespace or too short
    # Parse database URL and enforce SSL for Supabase and other cloud providers
    try:
        db_config = dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    except ValueError as e:
        import sys

        sys.stderr.write(
            "\n"
            "=" * 80 + "\n"
            f"❌ ERROR parsing DATABASE_URL: {e}\n"
            "\n"
            f"DATABASE_URL length: {len(DATABASE_URL)} chars\n"
            f"DATABASE_URL preview: {DATABASE_URL[:20]}...{DATABASE_URL[-20:]}\n"
            "\n"
            "Expected format:\n"
            "  postgresql://postgres:PASSWORD@db.PROJECT.supabase.co:5432/postgres?sslmode=require\n"
            "\n"
            "Please check your DATABASE_URL in Render environment variables.\n"
            "=" * 80 + "\n"
        )
        raise

    # Ensure SSL is enabled for secure connections (required by Supabase)
    if "OPTIONS" not in db_config:
        db_config["OPTIONS"] = {}

    # Force SSL mode if not already specified in the URL
    if "sslmode" not in DATABASE_URL.lower():
        db_config["OPTIONS"]["sslmode"] = "require"

    DATABASES = {"default": db_config}
else:
    # Default database configuration for local development
    # WARNING: This will fail on Render if DATABASE_URL is not set!
    import sys

    if os.environ.get("ON_RENDER"):
        sys.stderr.write(
            "\n"
            "=" * 80 + "\n"
            "❌ ERROR: DATABASE_URL environment variable is not set!\n"
            "\n"
            "You need to add DATABASE_URL to your Render service:\n"
            "1. Go to Render Dashboard → Your Service → Environment\n"
            "2. Add environment variable: DATABASE_URL\n"
            "3. Set value to your Supabase connection string:\n"
            "   postgresql://postgres:PASSWORD@db.PROJECT.supabase.co:5432/postgres?sslmode=require\n"
            "\n"
            "Your Supabase URL should be:\n"
            "   postgresql://postgres:tabio4545@db.enzpcumjosskxgpnahnk.supabase.co:5432/postgres?sslmode=require\n"
            "\n"
            "Or use the render.yaml blueprint which prompts for this automatically.\n"
            "=" * 80 + "\n"
        )
        raise ValueError(
            "DATABASE_URL environment variable is required on Render. "
            "Please add it to your service environment variables."
        )

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
