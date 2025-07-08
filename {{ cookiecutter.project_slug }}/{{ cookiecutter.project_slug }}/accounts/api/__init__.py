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
from {{ cookiecutter.project_slug }}.accounts.api.oauth2 import router as oauth2_router
from {{ cookiecutter.project_slug }}.accounts.api.users import router as users_router

__all__ = [
    'auth_router',
    'oauth2_router', 
    'users_router',
]

# Initialize the main accounts router
router = Router()

# Include all account-related API routers
router.add_router("/auth", auth_router, tags=["Authentication"])
router.add_router("/oauth2", oauth2_router, tags=["OAuth2"])
router.add_router("/users", users_router, tags=["Users"])
