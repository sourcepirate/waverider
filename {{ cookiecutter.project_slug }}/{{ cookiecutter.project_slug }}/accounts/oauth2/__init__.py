"""
OAuth2 Authentication Package

This package provides OAuth2 authentication functionality for Google, GitHub, and Facebook providers.
It includes provider configuration, user data normalization, and API endpoints.
"""

from {{ cookiecutter.project_slug }}.accounts.oauth2.providers import OAUTH2_PROVIDERS, get_oauth2_config
from {{ cookiecutter.project_slug }}.accounts.oauth2.utils import exchange_code_for_token, get_user_info, normalize_user_data
from {{ cookiecutter.project_slug }}.accounts.oauth2.api import router as oauth2_router

__all__ = [
    'OAUTH2_PROVIDERS',
    'get_oauth2_config',
    'exchange_code_for_token',
    'get_user_info',
    'normalize_user_data',
    'oauth2_router',
]
