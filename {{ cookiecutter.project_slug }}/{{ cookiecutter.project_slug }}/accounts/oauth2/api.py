"""
OAuth2 API Endpoints

This module contains Django Ninja API endpoints for OAuth2 authentication.
"""

import secrets
import urllib.parse
from ninja import Router
from django.contrib.auth.models import User
from django.core.cache import cache
from rest_framework_simplejwt.tokens import RefreshToken
import requests

from {{ cookiecutter.project_slug }}.accounts.oauth2.schemas import (
    OAuth2AuthorizeSchema,
    OAuth2CallbackSchema,
    OAuth2TokenResponseSchema,
    OAuth2ErrorSchema,
    OAuth2ProvidersResponseSchema,
    OAuth2AuthorizeResponseSchema,
)
from {{ cookiecutter.project_slug }}.accounts.oauth2.providers import get_oauth2_config, get_available_providers
from {{ cookiecutter.project_slug }}.accounts.oauth2.utils import exchange_code_for_token, get_user_info, normalize_user_data

# Initialize the OAuth2 router
router = Router()


@router.get(
    "/providers",
    response={200: OAuth2ProvidersResponseSchema},
    summary="Get list of available OAuth2 providers"
)
def oauth2_providers(request):
    """
    Get list of configured OAuth2 providers.
    
    Returns a list of OAuth2 providers that have been configured
    with valid client credentials.
    """
    available_providers = get_available_providers()
    
    return 200, {
        "providers": available_providers
    }


@router.post(
    "/authorize",
    response={200: OAuth2AuthorizeResponseSchema, 400: OAuth2ErrorSchema},
    summary="Get OAuth2 authorization URL"
)
def oauth2_authorize(request, payload: OAuth2AuthorizeSchema):
    """
    Generate OAuth2 authorization URL for specified provider.
    
    This endpoint generates the URL where the user should be redirected
    for OAuth2 authentication. It also handles CSRF protection using
    the state parameter.
    """
    try:
        config = get_oauth2_config(payload.provider)
    except ValueError as e:
        return 400, {"error": "invalid_provider", "error_description": str(e)}
    
    # Generate state for CSRF protection
    state = payload.state or secrets.token_urlsafe(32)
    
    # Cache the state and redirect_uri for verification
    cache_key = f"oauth2_state_{state}"
    cache.set(cache_key, {
        'provider': payload.provider,
        'redirect_uri': payload.redirect_uri
    }, timeout=600)  # 10 minutes
    
    # Build authorization URL
    params = {
        'client_id': config['client_id'],
        'redirect_uri': payload.redirect_uri,
        'scope': config['scope'],
        'response_type': 'code',
        'state': state,
    }
    
    if payload.provider == 'google':
        params['access_type'] = 'offline'
        params['prompt'] = 'consent'
    
    auth_url = f"{config['authorization_url']}?{urllib.parse.urlencode(params)}"
    
    return 200, {
        "authorization_url": auth_url,
        "state": state
    }


@router.post(
    "/callback",
    response={200: OAuth2TokenResponseSchema, 400: OAuth2ErrorSchema, 401: OAuth2ErrorSchema},
    summary="Handle OAuth2 callback and authenticate user"
)
def oauth2_callback(request, payload: OAuth2CallbackSchema):
    """
    Handle OAuth2 callback, exchange code for token, and authenticate/create user.
    
    This endpoint handles the OAuth2 callback from the provider, exchanges
    the authorization code for an access token, retrieves user information,
    and either finds an existing user or creates a new one. Returns JWT tokens
    for the authenticated user.
    """
    # Verify state parameter for CSRF protection
    if payload.state:
        cache_key = f"oauth2_state_{payload.state}"
        cached_data = cache.get(cache_key)
        if not cached_data:
            return 400, {
                "error": "invalid_state", 
                "error_description": "State parameter is invalid or expired"
            }
        
        if (cached_data['provider'] != payload.provider or 
            cached_data['redirect_uri'] != payload.redirect_uri):
            return 400, {
                "error": "state_mismatch", 
                "error_description": "State parameters do not match"
            }
        
        # Clean up the state
        cache.delete(cache_key)
    
    try:
        # Exchange code for access token
        token_response = exchange_code_for_token(
            payload.provider, 
            payload.code, 
            payload.redirect_uri
        )
        access_token = token_response.get('access_token')
        
        if not access_token:
            return 400, {
                "error": "token_exchange_failed", 
                "error_description": "Failed to obtain access token"
            }
        
        # Get user information from OAuth2 provider
        user_info = get_user_info(payload.provider, access_token)
        normalized_data = normalize_user_data(payload.provider, user_info, access_token)
        
        if not normalized_data.get('email'):
            return 400, {
                "error": "no_email", 
                "error_description": "Email address is required but not provided by the OAuth2 provider"
            }
        
        # Find or create user
        user = _find_or_create_user(normalized_data)
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return 200, {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': user
        }
        
    except requests.RequestException as e:
        return 400, {
            "error": "api_error", 
            "error_description": f"OAuth2 API request failed: {str(e)}"
        }
    except ValueError as e:
        return 400, {
            "error": "invalid_provider", 
            "error_description": str(e)
        }
    except Exception as e:
        return 400, {
            "error": "unexpected_error", 
            "error_description": "An unexpected error occurred during authentication"
        }


def _find_or_create_user(normalized_data: dict) -> User:
    """
    Find existing user by email or create a new one.
    
    Args:
        normalized_data: Normalized user data from OAuth2 provider
        
    Returns:
        User instance (existing or newly created)
    """
    email = normalized_data['email']
    username = normalized_data['username']
    
    # Try to find existing user by email
    try:
        user = User.objects.get(email=email)
        return user
    except User.DoesNotExist:
        # Create new user
        # Ensure username is unique
        base_username = username or email.split('@')[0]
        final_username = base_username
        counter = 1
        while User.objects.filter(username=final_username).exists():
            final_username = f"{base_username}{counter}"
            counter += 1
        
        user = User.objects.create_user(
            username=final_username,
            email=email,
            first_name=normalized_data.get('first_name', ''),
            last_name=normalized_data.get('last_name', ''),
            password=None  # OAuth2 users don't have passwords
        )
        user.set_unusable_password()
        user.save()
        
        return user
