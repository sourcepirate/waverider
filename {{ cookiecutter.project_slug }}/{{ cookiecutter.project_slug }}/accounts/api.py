"""
Accounts module API configuration.

This module provides a central location for API-related imports
and configuration for the accounts application.
"""

from .api.auth import *  # noqa: F401, F403
from .api.oauth2 import *  # noqa: F401, F403
from .api.users import *  # noqa: F401, F403

__all__ = [
    # Authentication APIs
    'auth',
    # OAuth2 APIs  
    'oauth2',
    # User management APIs
    'users',
]
