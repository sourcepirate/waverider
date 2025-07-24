"""
OAuth2 Utility Functions

This module contains utility functions for OAuth2 token exchange,
user information retrieval, and data normalization.
"""

import requests
from typing import Dict, Any
from .providers import get_oauth2_config


def exchange_code_for_token(provider: str, code: str, redirect_uri: str) -> Dict[str, Any]:
    """
    Exchange authorization code for access token.
    
    Args:
        provider: OAuth2 provider name
        code: Authorization code from provider
        redirect_uri: Redirect URI used in authorization
        
    Returns:
        Dict containing token response data
        
    Raises:
        requests.RequestException: If token exchange fails
        ValueError: If provider is invalid or not configured
    """
    config = get_oauth2_config(provider)
    
    data = {
        'client_id': config['client_id'],
        'client_secret': config['client_secret'],
        'code': code,
        'redirect_uri': redirect_uri,
    }
    
    if provider == 'google':
        data['grant_type'] = 'authorization_code'
    
    headers = {'Accept': 'application/json'}
    
    response = requests.post(config['token_url'], data=data, headers=headers)
    response.raise_for_status()
    
    return response.json()


def get_user_info(provider: str, access_token: str) -> Dict[str, Any]:
    """
    Get user information from OAuth2 provider.
    
    Args:
        provider: OAuth2 provider name
        access_token: OAuth2 access token
        
    Returns:
        Dict containing user information from provider
        
    Raises:
        requests.RequestException: If user info request fails
        ValueError: If provider is invalid or not configured
    """
    config = get_oauth2_config(provider)
    
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {}
    
    if provider == 'facebook':
        params['fields'] = 'id,email,first_name,last_name,name'
    
    response = requests.get(config['user_info_url'], headers=headers, params=params)
    response.raise_for_status()
    
    return response.json()


def normalize_user_data(provider: str, user_info: Dict[str, Any], access_token: Optional[str] = None) -> Dict[str, Any]:
    """
    Normalize user data from different OAuth2 providers to a common format.
    
    Args:
        provider: OAuth2 provider name
        user_info: Raw user information from provider
        access_token: OAuth2 access token (optional, needed for some providers)
        
    Returns:
        Dict containing normalized user data with keys:
        - email: User email address
        - first_name: User first name
        - last_name: User last name
        - username: Suggested username
        - provider_id: User ID from OAuth2 provider
    """
    if provider == 'google':
        return _normalize_google_data(user_info)
    elif provider == 'github':
        return _normalize_github_data(user_info, access_token)
    elif provider == 'facebook':
        return _normalize_facebook_data(user_info)
    
    return {}


def _normalize_google_data(user_info: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize Google OAuth2 user data."""
    return {
        'email': user_info.get('email'),
        'first_name': user_info.get('given_name', ''),
        'last_name': user_info.get('family_name', ''),
        'username': user_info.get('email', '').split('@')[0],
        'provider_id': user_info.get('id'),
    }


def _normalize_github_data(user_info: Dict[str, Any], access_token: str = None) -> Dict[str, Any]:
    """Normalize GitHub OAuth2 user data."""
    # For GitHub, we might need to make an additional request for email
    email = user_info.get('email')
    if not email and access_token:
        # GitHub users can hide their email, try to get public emails
        headers = {'Authorization': f'Bearer {access_token}'}
        try:
            email_response = requests.get('https://api.github.com/user/emails', headers=headers)
            if email_response.status_code == 200:
                emails = email_response.json()
                primary_email = next((e['email'] for e in emails if e['primary']), None)
                email = primary_email or emails[0]['email'] if emails else None
        except requests.RequestException:
            # If we can't get emails, continue without email
            pass
    
    return {
        'email': email,
        'first_name': user_info.get('name', '').split(' ')[0] if user_info.get('name') else '',
        'last_name': ' '.join(user_info.get('name', '').split(' ')[1:]) if user_info.get('name') else '',
        'username': user_info.get('login', ''),
        'provider_id': str(user_info.get('id')),
    }


def _normalize_facebook_data(user_info: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize Facebook OAuth2 user data."""
    return {
        'email': user_info.get('email'),
        'first_name': user_info.get('first_name', ''),
        'last_name': user_info.get('last_name', ''),
        'username': user_info.get('email', '').split('@')[0] if user_info.get('email') else '',
        'provider_id': user_info.get('id'),
    }
