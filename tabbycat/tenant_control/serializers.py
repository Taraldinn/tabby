"""
REST API Serializers for Tenant Management
===========================================

Serializers for tenant CRUD operations, user management, and analytics.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from tenants.models import Client, Domain
from django.utils import timezone


User = get_user_model()


class TenantOwnerSerializer(serializers.ModelSerializer):
    """Serializer for tenant owner (user) information."""

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "date_joined"]
        read_only_fields = fields


class DomainSerializer(serializers.ModelSerializer):
    """Serializer for tenant domains."""

    class Meta:
        model = Domain
        fields = ["id", "domain", "is_primary"]
        read_only_fields = ["id"]


class TenantListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for tenant list view.
    Optimized for performance with minimal data.
    """

    owner_username = serializers.CharField(source="owner.username", read_only=True)
    owner_email = serializers.EmailField(source="owner.email", read_only=True)
    primary_domain = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = [
            "id",
            "schema_name",
            "name",
            "owner_username",
            "owner_email",
            "primary_domain",
            "status",
            "plan",
            "total_tournaments",
            "total_users",
            "created_on",
            "last_activity",
        ]
        read_only_fields = fields

    def get_primary_domain(self, obj):
        """Get the primary domain for this tenant."""
        try:
            domain = obj.domain_set.filter(is_primary=True).first()
            return domain.domain if domain else None
        except Exception:
            return None

    def get_status(self, obj):
        """Get tenant status string."""
        if obj.is_suspended:
            return "suspended"
        elif obj.is_active:
            return "active"
        else:
            return "inactive"


class TenantDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for tenant detail view.
    Includes all fields, relationships, and computed data.
    """

    owner = TenantOwnerSerializer(read_only=True)
    domains = DomainSerializer(source="domain_set", many=True, read_only=True)
    status = serializers.SerializerMethodField()
    can_access = serializers.BooleanField(read_only=True)

    class Meta:
        model = Client
        fields = [
            "id",
            "schema_name",
            "name",
            "owner",
            "domains",
            "status",
            "can_access",
            "is_active",
            "is_suspended",
            "suspended_at",
            "plan",
            "storage_used_mb",
            "total_users",
            "total_tournaments",
            "created_on",
            "last_activity",
            "notes",
        ]
        read_only_fields = [
            "id",
            "schema_name",
            "owner",
            "suspended_at",
            "storage_used_mb",
            "total_users",
            "total_tournaments",
            "created_on",
            "last_activity",
        ]

    def get_status(self, obj):
        """Get tenant status string."""
        if obj.is_suspended:
            return "suspended"
        elif obj.is_active:
            return "active"
        else:
            return "inactive"


class TenantCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for manual tenant creation by super admin.
    Includes domain creation.
    """

    domain = serializers.CharField(write_only=True, required=True)
    owner_id = serializers.IntegerField(write_only=True, required=True)

    class Meta:
        model = Client
        fields = [
            "schema_name",
            "name",
            "owner_id",
            "domain",
            "plan",
            "is_active",
        ]

    def validate_schema_name(self, value):
        """Validate schema name is unique and valid."""
        if Client.objects.filter(schema_name=value).exists():
            raise serializers.ValidationError("Schema name already exists.")

        # Validate schema name format (PostgreSQL rules)
        import re

        if not re.match(r"^[a-z][a-z0-9_]{0,62}$", value):
            raise serializers.ValidationError(
                "Schema name must start with a letter and contain only lowercase letters, "
                "numbers, and underscores (max 63 characters)."
            )

        return value

    def validate_domain(self, value):
        """Validate domain is unique."""
        if Domain.objects.filter(domain=value).exists():
            raise serializers.ValidationError("Domain already exists.")
        return value

    def validate_owner_id(self, value):
        """Validate owner exists and doesn't have a tenant."""
        try:
            user = User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")

        if hasattr(user, "tenant"):
            raise serializers.ValidationError("User already has a tenant.")

        return value

    def create(self, validated_data):
        """Create tenant and domain."""
        domain_name = validated_data.pop("domain")
        owner_id = validated_data.pop("owner_id")

        # Get owner user
        owner = User.objects.get(id=owner_id)
        validated_data["owner"] = owner

        # Create tenant
        tenant = Client.objects.create(**validated_data)

        # Create domain
        Domain.objects.create(domain=domain_name, tenant=tenant, is_primary=True)

        return tenant


class TenantUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating tenant information."""

    class Meta:
        model = Client
        fields = [
            "name",
            "is_active",
            "plan",
            "notes",
        ]


class TenantSuspendSerializer(serializers.Serializer):
    """Serializer for suspending/unsuspending tenants."""

    suspend = serializers.BooleanField(required=True)
    reason = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        """Validate suspension data."""
        if data.get("suspend") and not data.get("reason"):
            raise serializers.ValidationError(
                {"reason": "Reason is required when suspending a tenant."}
            )
        return data


class TenantStatsSerializer(serializers.Serializer):
    """Serializer for tenant usage statistics."""

    total_tenants = serializers.IntegerField()
    active_tenants = serializers.IntegerField()
    suspended_tenants = serializers.IntegerField()
    total_storage_mb = serializers.FloatField()
    total_users = serializers.IntegerField()
    total_tournaments = serializers.IntegerField()
    tenants_by_plan = serializers.DictField()
    recent_signups = serializers.IntegerField()

    class Meta:
        fields = [
            "total_tenants",
            "active_tenants",
            "suspended_tenants",
            "total_storage_mb",
            "total_users",
            "total_tournaments",
            "tenants_by_plan",
            "recent_signups",
        ]


class ImpersonationTokenSerializer(serializers.Serializer):
    """Serializer for generating impersonation JWT tokens."""

    tenant_id = serializers.IntegerField(required=True)

    def validate_tenant_id(self, value):
        """Validate tenant exists."""
        try:
            Client.objects.get(id=value)
        except Client.DoesNotExist:
            raise serializers.ValidationError("Tenant not found.")
        return value
