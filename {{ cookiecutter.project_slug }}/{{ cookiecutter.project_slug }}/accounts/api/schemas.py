"""
API Schemas for User Management

Additional schemas for user profile management and API operations.
"""

from ninja import Schema
from pydantic import Field
from typing import Optional


class UserUpdateSchema(Schema):
    """Schema for updating user profile."""
    first_name: Optional[str] = Field(None, max_length=150)
    last_name: Optional[str] = Field(None, max_length=150)
    email: Optional[str] = Field(None, pattern=r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")


class UserPublicSchema(Schema):
    """Schema for public user information (excludes sensitive data)."""
    id: int
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    # Note: Email is excluded from public schema for privacy


class AuthTokenSchema(Schema):
    """Schema for authentication token information."""
    token_type: str = "Bearer"
    access_token: str
    expires_in: int = 3600  # 1 hour default


class PasswordChangeSchema(Schema):
    """Schema for password change requests."""
    old_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)


class PasswordResetRequestSchema(Schema):
    """Schema for password reset requests."""
    email: str = Field(..., pattern=r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")


class PasswordResetConfirmSchema(Schema):
    """Schema for password reset confirmation."""
    token: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)


class APISuccessSchema(Schema):
    """Schema for successful API operations."""
    success: bool = True
    message: str
