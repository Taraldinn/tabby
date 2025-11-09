"""
Tenant and Domain Models
=========================

Client: Represents a tenant with their own PostgreSQL schema
Domain: Maps subdomains/domains to tenants for routing
"""

from django.db import models
from django.contrib.auth import get_user_model
from django_tenants.models import TenantMixin, DomainMixin
from django.utils import timezone


User = get_user_model()


class Client(TenantMixin):
    """
    Tenant model representing a user's site.

    Each Client gets:
    - A unique PostgreSQL schema (auto-created)
    - A subdomain (username.myapp.com)
    - Isolated data (tournaments, teams, results, etc.)

    Inherits from TenantMixin:
    - schema_name: PostgreSQL schema name (auto-generated)
    - auto_create_schema: Whether to auto-create on save (default: True)
    """

    # Tenant metadata
    name = models.CharField(
        max_length=100, help_text="Display name for this tenant's site"
    )

    created_on = models.DateField(
        auto_now_add=True, help_text="Date this tenant was created"
    )

    # Owner relationship (one user owns one tenant)
    owner = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="tenant",
        help_text="User who owns this tenant site",
    )

    # Status management
    is_active = models.BooleanField(
        default=True, help_text="Whether this tenant is active (can access their site)"
    )

    is_suspended = models.BooleanField(
        default=False, help_text="Whether this tenant has been suspended by admin"
    )

    suspended_at = models.DateTimeField(
        null=True, blank=True, help_text="When this tenant was suspended"
    )

    # Subscription/billing (placeholder for future implementation)
    plan = models.CharField(
        max_length=20,
        default="free",
        choices=[
            ("free", "Free"),
            ("basic", "Basic"),
            ("pro", "Professional"),
            ("enterprise", "Enterprise"),
        ],
        help_text="Subscription plan for this tenant",
    )

    # Usage tracking
    storage_used_mb = models.FloatField(
        default=0.0, help_text="Storage used by this tenant in MB"
    )

    total_users = models.IntegerField(
        default=0, help_text="Total number of users in this tenant"
    )

    total_tournaments = models.IntegerField(
        default=0, help_text="Total number of tournaments created"
    )

    last_activity = models.DateTimeField(
        auto_now=True, help_text="Last time this tenant had any activity"
    )

    # Additional metadata
    notes = models.TextField(blank=True, help_text="Admin notes about this tenant")

    # Django-tenants required fields
    auto_create_schema = True  # Automatically create PostgreSQL schema on save
    auto_drop_schema = False  # Don't auto-delete schema (require explicit deletion)

    class Meta:
        verbose_name = "Tenant (Client)"
        verbose_name_plural = "Tenants (Clients)"
        ordering = ["-created_on"]
        indexes = [
            models.Index(fields=["schema_name"]),
            models.Index(fields=["owner"]),
            models.Index(fields=["is_active", "is_suspended"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.schema_name})"

    def suspend(self):
        """Suspend this tenant (admin action)."""
        self.is_suspended = True
        self.suspended_at = timezone.now()
        self.save(update_fields=["is_suspended", "suspended_at"])

    def unsuspend(self):
        """Unsuspend this tenant (admin action)."""
        self.is_suspended = False
        self.suspended_at = None
        self.save(update_fields=["is_suspended", "suspended_at"])

    def can_access(self):
        """Check if tenant can access their site."""
        return self.is_active and not self.is_suspended

    def update_usage_stats(self):
        """
        Update usage statistics for this tenant.
        Call this periodically or after significant changes.
        """
        from django_tenants.utils import schema_context

        with schema_context(self.schema_name):
            # Update user count
            from django.contrib.auth import get_user_model

            User = get_user_model()
            self.total_users = User.objects.count()

            # Update tournament count
            try:
                from tournaments.models import Tournament

                self.total_tournaments = Tournament.objects.count()
            except ImportError:
                pass  # Tournament model not available

            self.save(
                update_fields=["total_users", "total_tournaments", "last_activity"]
            )


class Domain(DomainMixin):
    """
    Domain model mapping domains/subdomains to tenants.

    Examples:
    - admin.myapp.com → public schema (super admin)
    - john.myapp.com → john's tenant schema
    - jane.myapp.com → jane's tenant schema

    Inherits from DomainMixin:
    - domain: The domain/subdomain string
    - tenant: ForeignKey to Client
    - is_primary: Whether this is the primary domain for the tenant
    """

    class Meta:
        verbose_name = "Domain"
        verbose_name_plural = "Domains"
        ordering = ["domain"]

    def __str__(self):
        return f"{self.domain} → {self.tenant.name}"

    @staticmethod
    def get_tenant_from_subdomain(subdomain):
        """
        Get tenant from subdomain string.
        Returns None if not found or if it's the admin subdomain.
        """
        from django.conf import settings

        # Don't return tenant for admin subdomain
        if subdomain == settings.ADMIN_SUBDOMAIN:
            return None

        # Find domain matching subdomain pattern
        full_domain = f"{subdomain}.{settings.TENANT_BASE_DOMAIN}"

        try:
            domain = Domain.objects.select_related("tenant").get(domain=full_domain)
            return domain.tenant if domain.tenant.can_access() else None
        except Domain.DoesNotExist:
            return None
