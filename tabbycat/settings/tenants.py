"""
Django-Tenants Configuration for Multi-Tenant SaaS
===================================================

This module configures django-tenants for schema-based multi-tenancy.
Each tenant gets their own PostgreSQL schema for data isolation.

Key Concepts:
- Shared apps: Accessible from all schemas (auth, users, tenants, domains)
- Tenant apps: Isolated per tenant (tournaments, teams, results, etc.)
- Public schema: Shared data and authentication
- Tenant schemas: Individual user sites (username.myapp.com)
"""

from .core import *  # noqa: F401, F403

# ==============================================================================
# Django-Tenants Configuration
# ==============================================================================

# The public schema stores shared data (users, tenant metadata, domains)
TENANT_MODEL = "tenants.Client"  # Your custom tenant model
TENANT_DOMAIN_MODEL = "tenants.Domain"  # Your custom domain model

# Apps that should be available in ALL schemas (public + tenant schemas)
# These are typically Django core apps and auth-related apps
SHARED_APPS = [
    "django_tenants",  # Must be first
    "daphne",
    "jet",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django_summernote",
    # Multi-tenancy management apps (in public schema only)
    "tenants",  # Tenant and Domain models
    "tenant_control",  # Super admin dashboard backend
    "users",  # User authentication and profiles
    # Shared utilities
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_simplejwt",
    "corsheaders",
    "django_extensions",
    # For initial setup, include all Tabbycat apps in shared
    # These will be migrated to tenant-only in future iterations
    "channels",
    "actionlog",
    "adjallocation",
    "adjfeedback",
    "api",
    "availability",
    "breakqual",
    "checkins",
    "divisions",
    "draw",
    "motions",
    "options",
    "participants",
    "printing",
    "privateurls",
    "results",
    "tournaments",
    "venues",
    "utils",
    "standings",
    "notifications",
    "importer",
    "registration",
    "dynamic_preferences",
    "gfklookupwidget",
    "formtools",
    "statici18n",
    "polymorphic",
    "drf_spectacular",
    "django_better_admin_arrayfield",
]

# Apps that should only be available in TENANT schemas
# These contain tenant-specific data (tournaments, teams, results, etc.)
# For now, keeping empty - we'll migrate apps here once base setup works
TENANT_APPS = [
    "django.contrib.contenttypes",  # Required in tenant schemas
]

# Combined installed apps (django-tenants requires this structure)
INSTALLED_APPS = list(SHARED_APPS) + [
    app for app in TENANT_APPS if app not in SHARED_APPS
]

# ==============================================================================
# Middleware Configuration
# ==============================================================================

# Django-tenants middleware must be first to set the correct schema
MIDDLEWARE = [
    "django_tenants.middleware.main.TenantMainMiddleware",  # Must be FIRST
    "django.middleware.gzip.GZipMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.http.ConditionalGetMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "utils.middleware.DebateMiddleware",
]

# ==============================================================================
# Database Configuration with Tenants
# ==============================================================================

# Use the tenant-aware database backend
DATABASES["default"]["ENGINE"] = "django_tenants.postgresql_backend"

# Connection and pooling settings for production
DATABASES["default"]["ATOMIC_REQUESTS"] = True
DATABASES["default"]["CONN_MAX_AGE"] = 60  # Connection pooling

# PostgreSQL search path handling
DATABASE_ROUTERS = ["django_tenants.routers.TenantSyncRouter"]

# ==============================================================================
# Public Schema Configuration
# ==============================================================================

# The public schema is for shared resources (not tenant-specific)
# This is where you'll access the admin dashboard at admin.myapp.com
PUBLIC_SCHEMA_URLCONF = "urls_public"  # We'll create this file

# ==============================================================================
# Tenant-Specific Settings
# ==============================================================================

# Each tenant will automatically get isolated in their own schema
# Settings below control tenant creation and domain routing

# Domain configuration
# In production, set these in environment variables:
# - TENANT_BASE_DOMAIN: Your main domain (e.g., "myapp.com")
# - ADMIN_SUBDOMAIN: Subdomain for super admin (e.g., "admin")
TENANT_BASE_DOMAIN = os.environ.get(
    "TENANT_BASE_DOMAIN", "localhost:8000"
)  # noqa: F405
ADMIN_SUBDOMAIN = os.environ.get("ADMIN_SUBDOMAIN", "admin")

# Subdomain configuration
# If True, tenants must be accessed via subdomain (e.g., user1.myapp.com)
# If False, tenants can be accessed via path (e.g., myapp.com/user1)
HAS_MULTI_TYPE_TENANTS = False  # We only have tenant schemas, no multi-type
TENANT_SUBFOLDER_PREFIX = ""  # Use subdomains, not folders

# ==============================================================================
# REST Framework JWT Configuration
# ==============================================================================

from datetime import timedelta  # noqa: E402

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",  # JWT for APIs
        "rest_framework.authentication.SessionAuthentication",  # Session for browsable API
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "drf_link_header_pagination.LinkHeaderLimitOffsetPagination",
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
    "TEST_REQUEST_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
}

# JWT Settings
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,  # noqa: F405
    "VERIFYING_KEY": None,
    "AUDIENCE": None,
    "ISSUER": None,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    # Include tenant information in JWT payload
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",
}

# ==============================================================================
# CORS Configuration for Vue Frontend
# ==============================================================================

# In production, configure these properly
CORS_ALLOW_ALL_ORIGINS = DEBUG  # noqa: F405
CORS_ALLOWED_ORIGINS = (
    os.environ.get(  # noqa: F405
        "CORS_ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000"
    ).split(",")
    if not DEBUG
    else []
)  # noqa: F405

CORS_ALLOW_CREDENTIALS = True
CORS_URLS_REGEX = r"^/(api|auth)/.*$"

# ==============================================================================
# Security Settings for Production
# ==============================================================================

# Override in production.py
if not DEBUG:  # noqa: F405
    # SSL/TLS settings
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"

    # HSTS settings
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # Proxy settings (for Nginx)
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    USE_X_FORWARDED_HOST = True
    USE_X_FORWARDED_PORT = True

# ==============================================================================
# Tenant Schema Limits (Optional)
# ==============================================================================

# You can set limits per tenant for storage, users, etc.
# These would be enforced in your business logic
TENANT_LIMITS = {
    "max_storage_mb": int(os.environ.get("TENANT_MAX_STORAGE_MB", 1000)),  # noqa: F405
    "max_users": int(os.environ.get("TENANT_MAX_USERS", 100)),  # noqa: F405
    "max_tournaments": int(os.environ.get("TENANT_MAX_TOURNAMENTS", 50)),  # noqa: F405
}

# ==============================================================================
# Logging Configuration
# ==============================================================================

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{levelname}] {asctime} {module} {process:d} {thread:d} | {message}",
            "style": "{",
        },
        "tenant": {
            "format": "[{levelname}] {asctime} [Tenant: %(schema_name)s] | {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "tenant_console": {
            "class": "logging.StreamHandler",
            "formatter": "tenant",
        },
    },
    "loggers": {
        "django_tenants": {
            "handlers": ["tenant_console"],
            "level": "INFO",
            "propagate": False,
        },
        "tenants": {
            "handlers": ["tenant_console"],
            "level": "INFO",
            "propagate": False,
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}
