"""
OAuth2 Provider Configuration

This module contains configuration for different OAuth2 providers including
their endpoints, scopes, and settings keys.
"""

from django.conf import settings
from typing import Dict, Any, List


# OAuth2 Provider Configuration
OAUTH2_PROVIDERS = {
    "google": {
        "authorization_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "user_info_url": "https://www.googleapis.com/oauth2/v2/userinfo",
        "scope": "openid email profile",
        "client_id_setting": "GOOGLE_OAUTH2_CLIENT_ID",
        "client_secret_setting": "GOOGLE_OAUTH2_CLIENT_SECRET",
    },
    "github": {
        "authorization_url": "https://github.com/login/oauth/authorize",
        "token_url": "https://github.com/login/oauth/access_token",
        "user_info_url": "https://api.github.com/user",
        "scope": "user:email",
        "client_id_setting": "GITHUB_OAUTH2_CLIENT_ID",
        "client_secret_setting": "GITHUB_OAUTH2_CLIENT_SECRET",
    },
    "facebook": {
        "authorization_url": "https://www.facebook.com/v18.0/dialog/oauth",
        "token_url": "https://graph.facebook.com/v18.0/oauth/access_token",
        "user_info_url": "https://graph.facebook.com/v18.0/me",
        "scope": "email,public_profile",
        "client_id_setting": "FACEBOOK_OAUTH2_CLIENT_ID",
        "client_secret_setting": "FACEBOOK_OAUTH2_CLIENT_SECRET",
    },
}


def get_oauth2_config(provider: str) -> Dict[str, Any]:
    """
    Get OAuth2 configuration for a provider.

    Args:
        provider: The OAuth2 provider name (google, github, facebook)

    Returns:
        Dict containing provider configuration with client credentials

    Raises:
        ValueError: If provider is not supported or credentials are not configured
    """
    if provider not in OAUTH2_PROVIDERS:
        raise ValueError(f"Unsupported OAuth2 provider: {provider}")

    config = OAUTH2_PROVIDERS[provider].copy()
    config["client_id"] = getattr(settings, config["client_id_setting"], None)
    config["client_secret"] = getattr(settings, config["client_secret_setting"], None)

    if not config["client_id"] or not config["client_secret"]:
        raise ValueError(f"OAuth2 credentials not configured for {provider}")

    return config


def get_available_providers() -> List[Dict[str, str]]:
    """
    Get list of OAuth2 providers that have been configured with credentials.

    Returns:
        List of provider dictionaries with name and scope
    """
    available_providers = []

    for provider_name, provider_config in OAUTH2_PROVIDERS.items():
        client_id = getattr(settings, provider_config["client_id_setting"], None)
        client_secret = getattr(
            settings, provider_config["client_secret_setting"], None
        )

        if client_id and client_secret:
            available_providers.append(
                {"name": provider_name, "scope": provider_config["scope"]}
            )

    return available_providers
