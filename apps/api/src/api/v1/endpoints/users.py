"""
User profile and management endpoints.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.logging import get_logger
from src.db.session import get_db_session
from src.crud.user import user_crud
from src.services.auth import get_current_active_user, require_admin
from src.services.storage import storage_service
from src.models.user import User
from src.schemas.user import (
    UserResponse,
    UserProfileUpdate,
    ReadingGoalsUpdate,
    UserSessionResponse,
    SessionListResponse,
)
from src.schemas.book import UserBookResponse
from src.schemas.common import MessageResponse
from src.exceptions.base import NotFoundException, BadRequestException

logger = get_logger(__name__)
router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
) -> UserResponse:
    """Get current user's profile."""
    return UserResponse.model_validate(current_user)


@router.patch("/me", response_model=UserResponse)
async def update_profile(
    data: UserProfileUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> UserResponse:
    """Update current user's profile."""
    updated = await user_crud.update_profile(db, user=current_user, obj_in=data)
    return UserResponse.model_validate(updated)


@router.post("/me/avatar", response_model=UserResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> UserResponse:
    """Upload user avatar."""
    # Validate image
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:  # 5MB limit
        raise BadRequestException("Image too large (max 5MB)")

    # Upload
    key = storage_service.generate_key("avatars", file.filename or "avatar.jpg", str(current_user.id))
    avatar_url = await storage_service.upload_file(
        contents, key, file.content_type or "image/jpeg"
    )

    current_user.avatar_url = avatar_url
    db.add(current_user)
    await db.flush()

    return UserResponse.model_validate(current_user)


@router.patch("/me/reading-goals", response_model=UserResponse)
async def update_reading_goals(
    data: ReadingGoalsUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> UserResponse:
    """Update reading goals."""
    updated = await user_crud.update_profile(
        db,
        user=current_user,
        obj_in=ReadingGoalsUpdate.model_validate(data),
    )
    return UserResponse.model_validate(updated)


@router.get("/me/library", response_model=list[UserBookResponse])
async def get_my_library(
    status: str | None = None,
    is_favorite: bool | None = None,
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> list[UserBookResponse]:
    """Get current user's library."""
    from src.crud.book import user_book_crud
    books, _ = await user_book_crud.get_user_library(
        db,
        user_id=current_user.id,
        status=status,
        is_favorite=is_favorite,
        limit=limit,
        offset=offset,
    )
    return [UserBookResponse.model_validate(b) for b in books]


@router.get("/me/continue-reading", response_model=list[UserBookResponse])
async def get_continue_reading(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> list[UserBookResponse]:
    """Get books to continue reading."""
    from src.crud.book import user_book_crud
    books = await user_book_crud.get_continue_reading(db, current_user.id)
    return [UserBookResponse.model_validate(b) for b in books]


@router.get("/me/sessions", response_model=SessionListResponse)
async def get_sessions(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> SessionListResponse:
    """Get active sessions."""
    from src.crud.user import user_session_crud
    sessions = await user_session_crud.get_active_sessions(db, current_user.id)
    return SessionListResponse(
        sessions=[UserSessionResponse.model_validate(s) for s in sessions],
        current_session_id=sessions[0].id if sessions else UUID("00000000-0000-0000-0000-000000000000"),
    )


@router.delete("/me/sessions/{session_id}", response_model=MessageResponse)
async def revoke_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> MessageResponse:
    """Revoke a session."""
    from src.crud.user import user_session_crud
    success = await user_session_crud.revoke_session(db, session_id, current_user.id)
    if not success:
        raise NotFoundException("Session")
    return MessageResponse(message="Session revoked")


@router.get("/{username}", response_model=UserResponse)
async def get_user_profile(
    username: str,
    db: AsyncSession = Depends(get_db_session),
) -> UserResponse:
    """Get public user profile."""
    user = await user_crud.get_by_username(db, username)
    if not user or not user.is_active:
        raise NotFoundException("User", username)
    return UserResponse.model_validate(user)


# ─── Admin Endpoints ──────────────────────────────────────────────

@router.get("/admin/list", response_model=list[UserResponse])
async def list_users(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db_session),
    admin: User = Depends(require_admin),
) -> list[UserResponse]:
    """List all users (admin only)."""
    users = await user_crud.get_multi(db, limit=limit, skip=offset)
    return [UserResponse.model_validate(u) for u in users]
