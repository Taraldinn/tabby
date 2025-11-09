"""Admin interface for tenant management."""

from django.contrib import admin
from django_tenants.admin import TenantAdminMixin
from .models import Client, Domain


@admin.register(Client)
class ClientAdmin(TenantAdminMixin, admin.ModelAdmin):
    """Admin interface for managing tenants."""

    list_display = [
        "name",
        "schema_name",
        "owner",
        "is_active",
        "is_suspended",
        "plan",
        "total_tournaments",
        "created_on",
    ]

    list_filter = [
        "is_active",
        "is_suspended",
        "plan",
        "created_on",
    ]

    search_fields = [
        "name",
        "schema_name",
        "owner__username",
        "owner__email",
    ]

    readonly_fields = [
        "schema_name",
        "created_on",
        "storage_used_mb",
        "total_users",
        "total_tournaments",
        "last_activity",
        "suspended_at",
    ]

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("name", "schema_name", "owner", "created_on")},
        ),
        ("Status", {"fields": ("is_active", "is_suspended", "suspended_at", "plan")}),
        (
            "Usage Statistics",
            {
                "fields": (
                    "storage_used_mb",
                    "total_users",
                    "total_tournaments",
                    "last_activity",
                ),
                "classes": ("collapse",),
            },
        ),
        ("Notes", {"fields": ("notes",), "classes": ("collapse",)}),
    )

    actions = ["suspend_tenants", "unsuspend_tenants", "update_stats"]

    def suspend_tenants(self, request, queryset):
        """Suspend selected tenants."""
        count = 0
        for tenant in queryset:
            tenant.suspend()
            count += 1
        self.message_user(request, f"Successfully suspended {count} tenant(s).")

    suspend_tenants.short_description = "Suspend selected tenants"

    def unsuspend_tenants(self, request, queryset):
        """Unsuspend selected tenants."""
        count = 0
        for tenant in queryset:
            tenant.unsuspend()
            count += 1
        self.message_user(request, f"Successfully unsuspended {count} tenant(s).")

    unsuspend_tenants.short_description = "Unsuspend selected tenants"

    def update_stats(self, request, queryset):
        """Update usage statistics for selected tenants."""
        count = 0
        for tenant in queryset:
            tenant.update_usage_stats()
            count += 1
        self.message_user(request, f"Successfully updated stats for {count} tenant(s).")

    update_stats.short_description = "Update usage statistics"


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    """Admin interface for managing domains."""

    list_display = [
        "domain",
        "tenant",
        "is_primary",
    ]

    list_filter = [
        "is_primary",
    ]

    search_fields = [
        "domain",
        "tenant__name",
        "tenant__schema_name",
    ]

    readonly_fields = []

    fieldsets = ((None, {"fields": ("domain", "tenant", "is_primary")}),)
