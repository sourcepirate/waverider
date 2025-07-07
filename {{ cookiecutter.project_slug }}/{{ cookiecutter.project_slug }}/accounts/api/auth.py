"""
Authentication API

This module contains authentication-related endpoints including:
- User registration
- User login
- JWT token management
"""

from ninja import Router
from django.contrib.auth import authenticate, login as django_login
from django.contrib.auth.models import User
from django.db import IntegrityError
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import timedelta

from {{ cookiecutter.project_slug }}.accounts.schemas import UserRegisterSchema, UserLoginSchema, TokenResponseSchema, UserSchema, ErrorSchema

# Initialize the authentication router
router = Router()


@router.post(
    "/register",
    response={201: UserSchema, 400: ErrorSchema, 409: ErrorSchema},
    summary="Register a new user"
)
def register(request, payload: UserRegisterSchema):
    """
    Registers a new user.
    Checks if username or email already exists.
    """
    try:
        if User.objects.filter(username=payload.username).exists():
            return 409, {"detail": "Username already exists."}
        if User.objects.filter(email=payload.email).exists():
            return 409, {"detail": "Email already registered."}

        user = User.objects.create_user(
            username=payload.username,
            email=payload.email,
            password=payload.password,
            first_name=payload.first_name or "",
            last_name=payload.last_name or ""
        )
        return 201, user # Automatically serialized to UserSchema
    except IntegrityError: # Catch potential race conditions
        return 409, {"detail": "Username or Email might already exist (race condition)."}
    except Exception as e:
        # Log the exception e
        return 400, {"detail": "Could not create user."}


@router.post(
    "/login",
    response={200: TokenResponseSchema, 401: ErrorSchema},
    summary="Authenticate user and return JWT tokens"
)
def login(request, payload: UserLoginSchema):
    """
    Authenticates a user based on username and password.
    Returns JWT access and refresh tokens upon successful authentication.
    """
    user = authenticate(username=payload.username, password=payload.password)
    if user is not None:
        # Optional: Log the user in for Django session-based features if needed
        # django_login(request, user)

        refresh = RefreshToken.for_user(user)
        return 200, {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }
    else:
        return 401, {"detail": "Invalid username or password."}

# Note: Token refresh and verification are handled by simplejwt's provided views (added in urls.py)
