"""
Users API

This module contains user profile management endpoints including:
- User profile retrieval
- User profile updates
- User management operations
"""

from ninja import Router
from django.contrib.auth.models import User
from ninja.security import HttpBearer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model

from {{ cookiecutter.project_slug }}.accounts.schemas import UserSchema, ErrorSchema

# Initialize the users router
router = Router()

# JWT Authentication for protected endpoints
class JWTAuth(HttpBearer):
    def authenticate(self, request, token):
        try:
            jwt_auth = JWTAuthentication()
            validated_token = jwt_auth.get_validated_token(token)
            user = jwt_auth.get_user(validated_token)
            return user
        except (InvalidToken, TokenError):
            return None

jwt_auth = JWTAuth()


@router.get(
    "/me",
    response={200: UserSchema, 401: ErrorSchema},
    summary="Get current user profile",
    auth=jwt_auth
)
def get_current_user(request):
    """
    Get the current authenticated user's profile.
    Requires a valid JWT token.
    """
    if not request.auth:
        return 401, {"detail": "Authentication required."}
    
    return 200, request.auth


@router.put(
    "/me",
    response={200: UserSchema, 400: ErrorSchema, 401: ErrorSchema},
    summary="Update current user profile",
    auth=jwt_auth
)
def update_current_user(request, payload: dict):
    """
    Update the current authenticated user's profile.
    Requires a valid JWT token.
    """
    if not request.auth:
        return 401, {"detail": "Authentication required."}
    
    user = request.auth
    
    # Update allowed fields
    if 'first_name' in payload:
        user.first_name = payload['first_name']
    if 'last_name' in payload:
        user.last_name = payload['last_name']
    if 'email' in payload:
        # Check if email is already taken by another user
        if User.objects.filter(email=payload['email']).exclude(id=user.id).exists():
            return 400, {"detail": "Email address is already in use."}
        user.email = payload['email']
    
    try:
        user.save()
        return 200, user
    except Exception as e:
        return 400, {"detail": "Failed to update user profile."}


@router.delete(
    "/me",
    response={204: None, 401: ErrorSchema},
    summary="Delete current user account",
    auth=jwt_auth
)
def delete_current_user(request):
    """
    Delete the current authenticated user's account.
    Requires a valid JWT token.
    """
    if not request.auth:
        return 401, {"detail": "Authentication required."}
    
    user = request.auth
    user.delete()
    return 204, None


@router.get(
    "/{user_id}",
    response={200: UserSchema, 404: ErrorSchema},
    summary="Get user profile by ID"
)
def get_user_by_id(request, user_id: int):
    """
    Get a user's public profile by their ID.
    Returns basic user information (excludes sensitive data).
    """
    try:
        user = User.objects.get(id=user_id)
        return 200, user
    except User.DoesNotExist:
        return 404, {"detail": "User not found."}
