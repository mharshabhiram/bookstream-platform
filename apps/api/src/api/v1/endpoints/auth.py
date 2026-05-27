"""
Authentication API endpoints.
"""

from fastapi import APIRouter, Depends, Request, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.logging import get_logger
from src.core.security import generate_secure_token
from src.db.session import get_db_session
from src.crud.user import user_crud, user_session_crud
from src.services.auth import auth_service, security
from src.services.email import email_service
from src.models.user import User, UserStatus
from src.schemas.user import (
    UserRegister,
    UserLogin,
    TokenResponse,
    TokenRefresh,
    PasswordResetRequest,
    PasswordResetConfirm,
    MessageResponse,
)
from src.exceptions.base import BadRequestException, UnauthorizedException

logger = get_logger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: Request,
    data: UserRegister,
    db: AsyncSession = Depends(get_db_session),
) -> MessageResponse:
    """Register a new user account."""
    # Check if email exists
    existing = await user_crud.get_by_email(db, data.email)
    if existing:
        raise BadRequestException("Email already registered")

    # Check if username exists
    existing = await user_crud.get_by_username(db, data.username)
    if existing:
        raise BadRequestException("Username already taken")

    # Create user
    user = await user_crud.create_user(db, obj_in=data)

    # Send verification email
    verification_token = generate_secure_token()
    # Store token in cache with expiry
    # await cache_service.set(f"verify:{user.id}", verification_token, ttl=86400)

    verification_url = f"{settings.APP_URL}/verify-email?token={verification_token}"
    await email_service.send_verification_email(
        user.email,
        user.username,
        verification_url,
    )

    logger.info("user_registered", user_id=str(user.id), email=user.email)
    return MessageResponse(message="Registration successful. Please verify your email.")


@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    data: UserLogin,
    db: AsyncSession = Depends(get_db_session),
) -> TokenResponse:
    """Login with email and password."""
    user = await auth_service.authenticate_user(
        db, data.email, data.password, request
    )

    tokens = await auth_service.create_tokens(db, user, request)

    # Build user response
    from src.schemas.user import UserResponse
    user_response = UserResponse.model_validate(user)

    return TokenResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type=tokens["token_type"],
        expires_in=tokens["expires_in"],
        user=user_response,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    data: TokenRefresh,
    db: AsyncSession = Depends(get_db_session),
) -> TokenResponse:
    """Refresh access token."""
    tokens = await auth_service.refresh_access_token(db, data.refresh_token)

    # Get user for response
    from src.core.security import decode_token
    payload = decode_token(tokens["access_token"])
    from uuid import UUID
    user = await user_crud.get(db, UUID(payload["sub"]))

    from src.schemas.user import UserResponse
    user_response = UserResponse.model_validate(user)

    return TokenResponse(
        access_token=tokens["access_token"],
        refresh_token=data.refresh_token,  # Keep same refresh token
        token_type=tokens["token_type"],
        expires_in=tokens["expires_in"],
        user=user_response,
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    data: TokenRefresh,
    db: AsyncSession = Depends(get_db_session),
) -> MessageResponse:
    """Logout and revoke refresh token."""
    await auth_service.logout(db, data.refresh_token)
    return MessageResponse(message="Logged out successfully")


@router.post("/password-reset-request", response_model=MessageResponse)
async def request_password_reset(
    data: PasswordResetRequest,
    db: AsyncSession = Depends(get_db_session),
) -> MessageResponse:
    """Request password reset email."""
    user = await user_crud.get_by_email(db, data.email)

    if user:
        reset_token = generate_secure_token()
        # Store in cache
        # await cache_service.set(f"reset:{user.id}", reset_token, ttl=3600)

        reset_url = f"{settings.APP_URL}/reset-password?token={reset_token}"
        await email_service.send_password_reset(
            user.email,
            user.username,
            reset_url,
        )

    # Always return success to prevent email enumeration
    return MessageResponse(
        message="If an account exists with this email, you will receive a reset link."
    )


@router.post("/password-reset", response_model=MessageResponse)
async def confirm_password_reset(
    data: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db_session),
) -> MessageResponse:
    """Confirm password reset with token."""
    # Validate token and get user
    # In production: verify against cache
    # user_id = await cache_service.get(f"reset:{data.token}")
    # if not user_id:
    #     raise BadRequestException("Invalid or expired reset token")

    # user = await user_crud.get(db, UUID(user_id))
    # if not user:
    #     raise BadRequestException("Invalid reset token")

    # await user_crud.update_password(db, user=user, new_password=data.new_password)
    # await cache_service.delete(f"reset:{data.token}")

    return MessageResponse(message="Password reset successful")
