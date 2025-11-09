"""
Tenant Creation Signals
========================

Automatically create tenant schema and domain when a user registers.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.conf import settings
import re


User = get_user_model()


def generate_schema_name(username):
    """
    Generate a valid PostgreSQL schema name from username.

    Rules:
    - Must start with letter
    - Only lowercase letters, numbers, underscores
    - No special characters
    - Max 63 characters (PostgreSQL limit)
    """
    # Convert to lowercase and replace invalid chars with underscore
    schema_name = re.sub(r"[^a-z0-9_]", "_", username.lower())

    # Ensure it starts with a letter
    if not schema_name[0].isalpha():
        schema_name = "tenant_" + schema_name

    # Truncate to 63 characters
    schema_name = schema_name[:63]

    # Remove trailing underscores
    schema_name = schema_name.rstrip("_")

    return schema_name


def generate_subdomain(username):
    """
    Generate a valid subdomain from username.

    Rules:
    - Only lowercase letters, numbers, hyphens
    - No special characters
    - Max 63 characters
    """
    subdomain = re.sub(r"[^a-z0-9-]", "-", username.lower())
    subdomain = subdomain.strip("-")
    subdomain = re.sub(r"-+", "-", subdomain)  # Remove multiple hyphens
    subdomain = subdomain[:63]

    return subdomain


@receiver(post_save, sender=User)
def create_tenant_on_user_signup(sender, instance, created, **kwargs):
    """
    Signal handler to automatically create a tenant when a user signs up.

    Flow:
    1. User registers (creates User instance)
    2. This signal fires
    3. Create Client (tenant) with unique schema
    4. Create Domain mapping subdomain to tenant
    5. Schema is automatically created by django-tenants

    Each user gets:
    - A PostgreSQL schema named after their username
    - A subdomain: username.myapp.com
    - Isolated tenant data
    """
    if not created:
        return  # Only run for newly created users

    # Skip if user already has a tenant
    if hasattr(instance, "tenant"):
        return

    # Skip for superusers (they use admin.myapp.com)
    if instance.is_superuser:
        return

    from .models import Client, Domain

    # Generate unique schema name
    schema_name = generate_schema_name(instance.username)

    # Ensure schema name is unique
    counter = 1
    original_schema = schema_name
    while Client.objects.filter(schema_name=schema_name).exists():
        schema_name = f"{original_schema}_{counter}"
        counter += 1

    try:
        # Create the tenant
        tenant = Client.objects.create(
            schema_name=schema_name,
            name=f"{instance.username}'s Site",
            owner=instance,
            is_active=True,
        )

        # Generate subdomain
        subdomain = generate_subdomain(instance.username)

        # Ensure subdomain is unique
        counter = 1
        original_subdomain = subdomain
        base_domain = settings.TENANT_BASE_DOMAIN
        full_domain = f"{subdomain}.{base_domain}"

        while Domain.objects.filter(domain=full_domain).exists():
            subdomain = f"{original_subdomain}{counter}"
            full_domain = f"{subdomain}.{base_domain}"
            counter += 1

        # Create the domain mapping
        Domain.objects.create(
            domain=full_domain,
            tenant=tenant,
            is_primary=True,
        )

        print(
            f"✅ Created tenant '{tenant.name}' with schema '{schema_name}' at {full_domain}"
        )

    except Exception as e:
        print(f"❌ Error creating tenant for user {instance.username}: {e}")
        # Don't raise exception - allow user creation to succeed even if tenant fails
        # Admin can manually create tenant later


@receiver(post_save, sender=User)
def update_tenant_on_user_change(sender, instance, created, **kwargs):
    """
    Update tenant metadata when user information changes.
    """
    if created:
        return  # Skip for new users (handled by create_tenant_on_user_signup)

    # Update tenant if user has one
    if hasattr(instance, "tenant"):
        tenant = instance.tenant

        # Update tenant name if username changed
        if tenant.name.endswith("'s Site"):
            tenant.name = f"{instance.username}'s Site"
            tenant.save(update_fields=["name"])
