#!/usr/bin/env python3
"""
Test script to verify email configuration in Django settings.
Run this to check if email settings are properly loaded from environment variables.
"""

import os
import sys
import django
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set the Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tabbycat.settings.render")

# Initialize Django
django.setup()

from django.conf import settings
from django.core.mail import send_mail


def test_email_settings():
    print("=== Email Configuration Test ===")
    print(f"EMAIL_BACKEND: {getattr(settings, 'EMAIL_BACKEND', 'NOT SET')}")
    print(f"EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'NOT SET')}")
    print(f"EMAIL_PORT: {getattr(settings, 'EMAIL_PORT', 'NOT SET')}")
    print(f"EMAIL_HOST_USER: {getattr(settings, 'EMAIL_HOST_USER', 'NOT SET')}")
    print(
        f"EMAIL_HOST_PASSWORD: {'***' if getattr(settings, 'EMAIL_HOST_PASSWORD', '') else 'NOT SET'}"
    )
    print(f"EMAIL_USE_TLS: {getattr(settings, 'EMAIL_USE_TLS', 'NOT SET')}")
    print(f"DEFAULT_FROM_EMAIL: {getattr(settings, 'DEFAULT_FROM_EMAIL', 'NOT SET')}")
    print(f"SERVER_EMAIL: {getattr(settings, 'SERVER_EMAIL', 'NOT SET')}")

    print("\n=== Environment Variables ===")
    email_env_vars = [
        "EMAIL_HOST",
        "EMAIL_PORT",
        "EMAIL_HOST_USER",
        "EMAIL_HOST_PASSWORD",
        "EMAIL_USE_TLS",
        "DEFAULT_FROM_EMAIL",
    ]
    for var in email_env_vars:
        value = os.environ.get(var, "NOT SET")
        if var == "EMAIL_HOST_PASSWORD" and value != "NOT SET":
            value = "***"
        print(f"{var}: {value}")

    print(
        f"\nDJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE', 'NOT SET')}"
    )


def test_email_send():
    """Test sending an actual email (optional)"""
    print("\n=== Email Send Test ===")

    # Check if all required settings are present
    required_settings = ["EMAIL_HOST", "EMAIL_HOST_USER", "EMAIL_HOST_PASSWORD"]
    missing_settings = []

    for setting in required_settings:
        if not getattr(settings, setting, None):
            missing_settings.append(setting)

    if missing_settings:
        print(
            f"Cannot test email sending - missing settings: {', '.join(missing_settings)}"
        )
        return

    try:
        # Try to send a test email
        send_mail(
            "Tabbycat Email Configuration Test",
            "This is a test email to verify email configuration is working.",
            settings.DEFAULT_FROM_EMAIL,
            [settings.DEFAULT_FROM_EMAIL],  # Send to self
            fail_silently=False,
        )
        print("✓ Test email sent successfully!")

    except Exception as e:
        print(f"✗ Email sending failed: {e}")
        print(f"Error type: {type(e).__name__}")


if __name__ == "__main__":
    test_email_settings()

    # Uncomment the line below to test actual email sending
    # test_email_send()
