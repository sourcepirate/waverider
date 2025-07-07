"""
OAuth2 Pydantic schemas for request/response validation.
"""

from ninja import Schema
from pydantic import Field
from typing import Optional
from ..schemas import UserSchema, ErrorSchema


class OAuth2AuthorizeSchema(Schema):
    """Schema for OAuth2 authorization request."""
    provider: str = Field(..., description="OAuth2 provider (google, github, facebook)")
    redirect_uri: str = Field(..., description="Redirect URI after authorization")
    state: Optional[str] = Field(None, description="CSRF protection state parameter")


class OAuth2CallbackSchema(Schema):
    """Schema for OAuth2 callback request."""
    provider: str = Field(..., description="OAuth2 provider")
    code: str = Field(..., description="Authorization code from provider")
    state: Optional[str] = Field(None, description="State parameter for CSRF protection")
    redirect_uri: str = Field(..., description="Redirect URI used in authorization")


class OAuth2TokenResponseSchema(Schema):
    """Schema for OAuth2 token response."""
    access: str
    refresh: str
    user: UserSchema


class OAuth2ErrorSchema(Schema):
    """Schema for OAuth2 error responses."""
    error: str
    error_description: Optional[str] = None


class OAuth2ProviderSchema(Schema):
    """Schema for OAuth2 provider information."""
    name: str
    scope: str


class OAuth2ProvidersResponseSchema(Schema):
    """Schema for OAuth2 providers list response."""
    providers: list[OAuth2ProviderSchema]


class OAuth2AuthorizeResponseSchema(Schema):
    """Schema for OAuth2 authorization URL response."""
    authorization_url: str
    state: str
