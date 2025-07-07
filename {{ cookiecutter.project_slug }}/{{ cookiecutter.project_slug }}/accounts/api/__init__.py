"""
Accounts API Package

This package contains all user-related API endpoints including:
- User authentication (login, register)
- OAuth2 authentication
- User profile management
- JWT token management
"""

from {{ cookiecutter.project_slug }}.accounts.api.auth import router as auth_router
from {{ cookiecutter.project_slug }}.accounts.api.oauth2 import router as oauth2_router
from {{ cookiecutter.project_slug }}.accounts.api.users import router as users_router

__all__ = [
    'auth_router',
    'oauth2_router', 
    'users_router',
]
