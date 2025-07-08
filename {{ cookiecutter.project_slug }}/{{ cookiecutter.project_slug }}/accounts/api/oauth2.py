"""
OAuth2 Authentication API

This module contains OAuth2 authentication endpoints including:
- OAuth2 provider management
- Authorization URL generation
- OAuth2 callback handling
"""

from ninja import Router

# Import the OAuth2 router from the oauth2 package
from {{ cookiecutter.project_slug }}.accounts.oauth2.api import router as oauth2_base_router

# Initialize the OAuth2 API router
router = Router()

# Include all OAuth2 endpoints
router.add_router("", oauth2_base_router)
