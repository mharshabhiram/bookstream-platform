"""
Authentication service with JWT, OAuth, and session management.
"""

from datetime import datetime, timezone, timedelta
from typing import Any
from uuid import UUID

from fastapi import Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_secure_token,
    verify_password,
)
from src.core.logging import get_logger
from src.db.session import get_db_session
from src.crud.user import user_crud, user_session_crud
from src.models.user import User, UserRole, UserStatus, UserSession
from src.exceptions.base import (
    UnauthorizedException,
    ForbiddenException,
    BadRequestException,
    TooManyRequestsException,
)

logger = get_logger(__name__)
security = HTTPBearer(auto_error=False)


class AuthService:
    """Authentication service."""

    def __init__(self):
        self.token_blacklist: set[str] = set()

    async def authenticate_user(
        self,
        db: AsyncSession,
        email: str,
        password: str,
        request: Request | None = None,
    ) -> User:
        """Authenticate user and return user object."""
        user = await user_crud.get_by_email(db, email)

        if not user:
            raise UnauthorizedException("Invalid email or password")

        # Check if account is locked
        if user.locked_until and user.locked_until > datetime.now(timezone.utc):
            raise TooManyRequestsException(
                f"Account locked until {user.locked_until.isoformat()}"
            )

        # Check if account is active
        if user.status != UserStatus.ACTIVE:
            raise UnauthorizedException("Account is not active")

        # Verify password
        if not user.hashed_password or not verify_password(password, user.hashed_password):
            if user:
                await user_crud.increment_failed_login(db, user=user)
            raise UnauthorizedException("Invalid email or password")

        # Update last login
        ip = request.client.host if request and request.client else None
        await user_crud.update_last_login(db, user=user, ip_address=ip)

        logger.info("user_authenticated", user_id=str(user.id))
        return user

    async def create_tokens(
        self,
        db: AsyncSession,
        user: User,
        request: Request | None = None,
    ) -> dict[str, Any]:
        """Create access and refresh tokens."""
        access_token = create_access_token(
            subject=str(user.id),
            extra_claims={
                "email": user.email,
                "username": user.username,
                "role": user.role.value,
            },
        )
        refresh_token = create_refresh_token(subject=str(user.id))

        # Store session
        ip = request.client.host if request and request.client else None
        user_agent = request.headers.get("user-agent") if request else None

        import hashlib
        refresh_hash = hashlib.sha256(refresh_token.encode()).hexdigest()

        session = UserSession(
            user_id=user.id,
            refresh_token_hash=refresh_hash,
            device_info=user_agent[:255] if user_agent else None,
            ip_address=ip,
            user_agent=user_agent,
            expires_at=datetime.now(timezone.utc) + timedelta(
                days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
            ),
        )
        db.add(session)
        await db.flush()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

    async def refresh_access_token(
        self,
        db: AsyncSession,
        refresh_token: str,
    ) -> dict[str, Any]:
        """Refresh access token using refresh token."""
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise UnauthorizedException("Invalid refresh token")

        user_id = UUID(payload["sub"])
        user = await user_crud.get(db, user_id)

        if not user or not user.is_active:
            raise UnauthorizedException("User not found or inactive")

        # Verify refresh token in database
        import hashlib
        refresh_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        session = await user_session_crud.get_by_refresh_token(db, refresh_hash)

        if not session or session.expires_at < datetime.now(timezone.utc):
            raise UnauthorizedException("Refresh token expired or revoked")

        # Create new tokens
        new_access = create_access_token(
            subject=str(user.id),
            extra_claims={
                "email": user.email,
                "username": user.username,
                "role": user.role.value,
            },
        )

        return {
            "access_token": new_access,
            "token_type": "bearer",
            "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

    async def logout(
        self,
        db: AsyncSession,
        refresh_token: str,
    ) -> None:
        """Logout user by revoking refresh token."""
        import hashlib
        refresh_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        session = await user_session_crud.get_by_refresh_token(db, refresh_hash)

        if session:
            session.is_active = False
            db.add(session)
            await db.flush()

        # Also blacklist the access token if provided
        self.token_blacklist.add(refresh_hash)

    async def get_current_user(
        self,
        db: AsyncSession,
        credentials: HTTPAuthorizationCredentials | None,
    ) -> User:
        """Get current user from JWT token."""
        if not credentials:
            raise UnauthorizedException("Authentication required")

        payload = decode_token(credentials.credentials)
        if not payload:
            raise UnauthorizedException("Invalid or expired token")

        user_id = UUID(payload["sub"])
        user = await user_crud.get(db, user_id)

        if not user or not user.is_active:
            raise UnauthorizedException("User not found or inactive")

        return user

    async def require_role(
        self,
        user: User,
        required_role: UserRole,
    ) -> None:
        """Check if user has required role."""
        role_hierarchy = {
            UserRole.USER: 1,
            UserRole.MODERATOR: 2,
            UserRole.ADMIN: 3,
        }

        if role_hierarchy.get(user.role, 0) < role_hierarchy.get(required_role, 0):
            raise ForbiddenException(
                f"This action requires {required_role.value} privileges"
            )


# Dependency for protected routes
async def get_current_user_dependency(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db_session),
) -> User:
    """FastAPI dependency to get current authenticated user."""
    auth_service = AuthService()
    return await auth_service.get_current_user(db, credentials)


async def get_current_active_user(
    current_user: User = Depends(get_current_user_dependency),
) -> User:
    """Ensure user is active."""
    if not current_user.is_active:
        raise UnauthorizedException("Account is not active")
    return current_user


async def require_admin(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Require admin role."""
    auth_service = AuthService()
    await auth_service.require_role(current_user, UserRole.ADMIN)
    return current_user


async def require_moderator(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Require moderator or admin role."""
    auth_service = AuthService()
    await auth_service.require_role(current_user, UserRole.MODERATOR)
    return current_user


# Singleton
auth_service = AuthService()
