"""
Main Accounts API Router

This module consolidates all user-related API endpoints.
"""

from ninja import Router
from {{ cookiecutter.project_slug }}.accounts.api import auth_router, oauth2_router, users_router

# Initialize the main accounts router
router = Router()

# Include all account-related API routers
router.add_router("/auth", auth_router, tags=["Authentication"])
router.add_router("/oauth2", oauth2_router, tags=["OAuth2"])
router.add_router("/users", users_router, tags=["Users"])