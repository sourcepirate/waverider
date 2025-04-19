from ninja import Schema
from pydantic import Field # Use Field for validation examples
import re
from typing import Optional

class UserRegisterSchema(Schema):
    username: str = Field(..., min_length=3, max_length=150)
    email: str = Field(..., pattern=r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)") # Basic email pattern
    password: str = Field(..., min_length=8)
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserLoginSchema(Schema):
    username: str
    password: str

class TokenResponseSchema(Schema):
    access: str
    refresh: str

# Schema for returning user details (excluding password)
class UserSchema(Schema):
    id: int
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class ErrorSchema(Schema):
    detail: str 