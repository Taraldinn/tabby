"""
Tenant Control App - Super Admin Dashboard Backend
===================================================

This app provides REST API endpoints for super admins to manage tenants:
- List all tenants with pagination
- View tenant details and usage statistics
- Suspend/unsuspend/delete tenants
- Impersonate tenants (generate JWT for tenant access)
- View analytics and usage metrics
"""

from django.apps import AppConfig


class TenantControlConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tenant_control"
    verbose_name = "Tenant Control (Super Admin)"
