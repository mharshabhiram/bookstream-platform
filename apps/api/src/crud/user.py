"""
User CRUD operations.
"""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import get_password_hash, verify_password
from src.core.logging import get_logger
from src.crud.base import BaseCRUD
from src.models.user import User, UserSession, OAuthAccount, UserStatus
from src.schemas.user import UserRegister, UserProfileUpdate

logger = get_logger(__name__)


class UserCRUD(BaseCRUD[User]):
    """User CRUD operations."""

    async def get_by_email(self, db: AsyncSession, email: str) -> User | None:
        """Get user by email."""
        result = await db.execute(
            select(User).where(User.email == email.lower())
        )
        return result.scalar_one_or_none()

    async def get_by_username(self, db: AsyncSession, username: str) -> User | None:
        """Get user by username."""
        result = await db.execute(
            select(User).where(User.username == username.lower())
        )
        return result.scalar_one_or_none()

    async def create_user(
        self,
        db: AsyncSession,
        *,
        obj_in: UserRegister,
    ) -> User:
        """Create a new user with hashed password."""
        db_obj = User(
            email=obj_in.email.lower(),
            username=obj_in.username.lower(),
            hashed_password=get_password_hash(obj_in.password),
            display_name=obj_in.display_name,
            status=UserStatus.PENDING_VERIFICATION,
        )
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        logger.info("user_created", user_id=str(db_obj.id), email=db_obj.email)
        return db_obj

    async def authenticate(
        self,
        db: AsyncSession,
        *,
        email: str,
        password: str,
    ) -> User | None:
        """Authenticate user with email and password."""
        user = await self.get_by_email(db, email)
        if not user:
            return None
        if not user.hashed_password:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def update_last_login(
        self,
        db: AsyncSession,
        *,
        user: User,
        ip_address: str | None = None,
    ) -> None:
        """Update user's last login timestamp."""
        user.last_login_at = datetime.now(timezone.utc)
        user.last_login_ip = ip_address
        user.failed_login_attempts = 0
        user.locked_until = None
        db.add(user)
        await db.flush()

    async def increment_failed_login(
        self,
        db: AsyncSession,
        *,
        user: User,
    ) -> None:
        """Increment failed login attempts."""
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= 5:
            user.locked_until = datetime.now(timezone.utc) + __import__("datetime").timedelta(minutes=30)
        db.add(user)
        await db.flush()

    async def update_profile(
        self,
        db: AsyncSession,
        *,
        user: User,
        obj_in: UserProfileUpdate,
    ) -> User:
        """Update user profile."""
        update_data = obj_in.model_dump(exclude_unset=True)
        return await self.update(db, db_obj=user, obj_in=update_data)

    async def update_password(
        self,
        db: AsyncSession,
        *,
        user: User,
        new_password: str,
    ) -> None:
        """Update user password."""
        user.hashed_password = get_password_hash(new_password)
        db.add(user)
        await db.flush()

    async def search_users(
        self,
        db: AsyncSession,
        *,
        query: str,
        limit: int = 20,
    ) -> list[User]:
        """Search users by username or display name."""
        result = await db.execute(
            select(User)
            .where(
                (User.username.ilike(f"%{query}%")) |
                (User.display_name.ilike(f"%{query}%"))
            )
            .where(User.status == UserStatus.ACTIVE)
            .where(User.deleted_at.is_(None))
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_user_stats(self, db: AsyncSession, user_id: UUID) -> dict:
        """Get user reading statistics."""
        from src.models.book import UserBook
        from src.models.reading import ReadingProgress

        # Books read
        books_read_result = await db.execute(
            select(func.count(UserBook.id))
            .where(UserBook.user_id == user_id)
            .where(UserBook.status == "completed")
        )
        books_read = books_read_result.scalar() or 0

        # Books reading
        books_reading_result = await db.execute(
            select(func.count(UserBook.id))
            .where(UserBook.user_id == user_id)
            .where(UserBook.status == "reading")
        )
        books_reading = books_reading_result.scalar() or 0

        # Total reading time
        time_result = await db.execute(
            select(func.sum(ReadingProgress.time_spent_seconds))
            .where(ReadingProgress.user_id == user_id)
        )
        total_time = time_result.scalar() or 0

        return {
            "total_books_read": books_read,
            "total_books_reading": books_reading,
            "total_reading_time_minutes": total_time // 60,
        }


class UserSessionCRUD(BaseCRUD[UserSession]):
    """User session CRUD operations."""

    async def get_by_refresh_token(
        self,
        db: AsyncSession,
        token_hash: str,
    ) -> UserSession | None:
        """Get session by refresh token hash."""
        result = await db.execute(
            select(UserSession)
            .where(UserSession.refresh_token_hash == token_hash)
            .where(UserSession.is_active == True)
        )
        return result.scalar_one_or_none()

    async def get_active_sessions(
        self,
        db: AsyncSession,
        user_id: UUID,
    ) -> list[UserSession]:
        """Get all active sessions for a user."""
        result = await db.execute(
            select(UserSession)
            .where(UserSession.user_id == user_id)
            .where(UserSession.is_active == True)
            .where(UserSession.expires_at > datetime.now(timezone.utc))
            .order_by(UserSession.last_used_at.desc())
        )
        return list(result.scalars().all())

    async def revoke_session(
        self,
        db: AsyncSession,
        session_id: UUID,
        user_id: UUID,
    ) -> bool:
        """Revoke a specific session."""
        result = await db.execute(
            update(UserSession)
            .where(UserSession.id == session_id)
            .where(UserSession.user_id == user_id)
            .values(is_active=False)
        )
        await db.flush()
        return result.rowcount > 0

    async def revoke_all_sessions(
        self,
        db: AsyncSession,
        user_id: UUID,
        except_session_id: UUID | None = None,
    ) -> None:
        """Revoke all user sessions except current."""
        query = (
            update(UserSession)
            .where(UserSession.user_id == user_id)
            .where(UserSession.is_active == True)
        )
        if except_session_id:
            query = query.where(UserSession.id != except_session_id)

        await db.execute(query.values(is_active=False))
        await db.flush()


class OAuthAccountCRUD(BaseCRUD[OAuthAccount]):
    """OAuth account CRUD operations."""

    async def get_by_provider(
        self,
        db: AsyncSession,
        provider: str,
        provider_account_id: str,
    ) -> OAuthAccount | None:
        """Get OAuth account by provider and account ID."""
        result = await db.execute(
            select(OAuthAccount)
            .where(OAuthAccount.provider == provider)
            .where(OAuthAccount.provider_account_id == provider_account_id)
        )
        return result.scalar_one_or_none()


# Singleton instances
user_crud = UserCRUD(User)
user_session_crud = UserSessionCRUD(UserSession)
oauth_account_crud = OAuthAccountCRUD(OAuthAccount)
