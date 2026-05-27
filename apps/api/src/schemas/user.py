"""
User Pydantic schemas for request/response validation.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from src.models.user import UserRole, UserStatus


# ─── Base Schemas ──────────────────────────────────────────────────

class UserBase(BaseModel):
    """Base user schema with common fields."""
    model_config = ConfigDict(from_attributes=True)

    username: str = Field(..., min_length=3, max_length=50)
    display_name: str | None = Field(None, max_length=100)
    bio: str | None = Field(None, max_length=2000)
    location: str | None = Field(None, max_length=100)
    website: str | None = Field(None, max_length=255)
    avatar_url: str | None = None
    preferred_language: str = "en"
    theme: str = "system"


class UserProfile(UserBase):
    """Public user profile schema."""
    id: UUID
    role: UserRole
    created_at: datetime
    follower_count: int = 0
    following_count: int = 0


class UserResponse(UserProfile):
    """Full user response with reading stats."""
    daily_reading_goal_minutes: int | None = None
    weekly_reading_goal_minutes: int | None = None
    last_login_at: datetime | None = None


# ─── Auth Schemas ──────────────────────────────────────────────────

class UserRegister(BaseModel):
    """User registration request."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    password: str = Field(..., min_length=8, max_length=128)
    display_name: str | None = Field(None, max_length=100)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserLogin(BaseModel):
    """User login request."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class TokenRefresh(BaseModel):
    """Token refresh request."""
    refresh_token: str


class PasswordResetRequest(BaseModel):
    """Password reset request."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation."""
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)


class ChangePassword(BaseModel):
    """Change password request."""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)


# ─── Profile Update ────────────────────────────────────────────────

class UserProfileUpdate(BaseModel):
    """User profile update request."""
    display_name: str | None = Field(None, max_length=100)
    bio: str | None = Field(None, max_length=2000)
    location: str | None = Field(None, max_length=100)
    website: str | None = Field(None, max_length=255)
    preferred_language: str | None = None
    theme: str | None = None
    daily_reading_goal_minutes: int | None = Field(None, ge=5, le=480)
    weekly_reading_goal_minutes: int | None = Field(None, ge=30, le=3360)


class ReadingGoalsUpdate(BaseModel):
    """Reading goals update."""
    daily_reading_goal_minutes: int = Field(..., ge=5, le=480)
    weekly_reading_goal_minutes: int = Field(..., ge=30, le=3360)


# ─── OAuth Schemas ─────────────────────────────────────────────────

class OAuthLogin(BaseModel):
    """OAuth login request."""
    provider: str = Field(..., pattern=r"^(google|github)$")
    code: str
    redirect_uri: str


class OAuthAccountResponse(BaseModel):
    """OAuth account response."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    provider: str
    provider_account_id: str
    created_at: datetime


# ─── Session Schemas ───────────────────────────────────────────────

class UserSessionResponse(BaseModel):
    """User session response."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    device_info: str | None
    ip_address: str | None
    is_active: bool
    created_at: datetime
    last_used_at: datetime


class SessionListResponse(BaseModel):
    """List of user sessions."""
    sessions: list[UserSessionResponse]
    current_session_id: UUID
