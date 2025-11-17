"""
=============================================================================
AI Hub - User Pydantic Schemas
=============================================================================
Request and response models for user-related endpoints.
=============================================================================
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
import uuid


class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr = Field(..., description="User's email address")
    full_name: str = Field(..., min_length=2, max_length=255, description="Full name")


class UserCreate(UserBase):
    """Schema for user registration."""
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Password (min 8 characters)"
    )
    phone_number: Optional[str] = Field(
        None,
        pattern=r'^\+?[1-9]\d{1,14}$',
        description="Phone number for SMS notifications (E.164 format)"
    )


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    phone_number: Optional[str] = None
    risk_tolerance: Optional[str] = Field(None, pattern="^(conservative|moderate|aggressive)$")
    email_notifications: Optional[bool] = None
    sms_notifications: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for user in API responses."""
    id: uuid.UUID
    phone_number: Optional[str] = None
    risk_tolerance: str
    email_notifications: bool
    sms_notifications: bool
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"
