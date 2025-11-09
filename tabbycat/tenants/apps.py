"""
Tenants App - Multi-Tenant Schema Management
=============================================

This app manages tenant (client) creation, domain routing, and schema isolation.
Each tenant represents a user's site with its own PostgreSQL schema.
"""

from django.apps import AppConfig


class TenantsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tenants"
    verbose_name = "Multi-Tenant Management"

    def ready(self):
        """Import signals when app is ready."""
        import tenants.signals  # noqa: F401
