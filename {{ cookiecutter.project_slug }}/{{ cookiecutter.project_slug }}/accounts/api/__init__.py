"""
Accounts API Package

This package contains all user-related API endpoints including:
- User authentication (login, register)
- OAuth2 authentication
- User profile management
- JWT token management
"""
from ninja import Router

from {{ cookiecutter.project_slug }}.accounts.api.auth import router as auth_router
{% if cookiecutter.include_oauth2 == 'y' %}
from {{ cookiecutter.project_slug }}.accounts.api.oauth2 import router as oauth2_router
{% endif %}
from {{ cookiecutter.project_slug }}.accounts.api.users import router as users_router

__all__ = [
    'auth_router',
{% if cookiecutter.include_oauth2 == 'y' %}
    'oauth2_router',
{% endif %}
    'users_router',
]

# Initialize the main accounts router
router = Router()

# Include all account-related API routers
router.add_router("/auth", auth_router, tags=["Authentication"])
{% if cookiecutter.include_oauth2 == 'y' %}
router.add_router("/oauth2", oauth2_router, tags=["OAuth2"])
{% endif %}
router.add_router("/users", users_router, tags=["Users"])
