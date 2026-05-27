"""
User model with authentication, profile, and social features.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
    JSON,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.session import Base

if TYPE_CHECKING:
    from src.models.book import UserBook
    from src.models.social import Follow, Review, Comment
    from src.models.reading import ReadingProgress, Highlight, Bookmark, Note
    from src.models.library import Shelf, Collection
    from src.models.analytics import ReadingSession
    from src.models.notification import Notification


class UserRole(str, Enum):
    """User role enumeration."""
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"


class UserStatus(str, Enum):
    """User account status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"


class User(Base):
    """User account model."""

    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )
    hashed_password: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # Profile
    display_name: Mapped[str | None] = mapped_column(String(100))
    avatar_url: Mapped[str | None] = mapped_column(String(500))
    bio: Mapped[str | None] = mapped_column(Text)
    location: Mapped[str | None] = mapped_column(String(100))
    website: Mapped[str | None] = mapped_column(String(255))

    # Preferences
    preferred_language: Mapped[str] = mapped_column(String(10), default="en")
    theme: Mapped[str] = mapped_column(String(20), default="system")

    # Status & Role
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role", create_type=False),
        default=UserRole.USER,
        nullable=False,
    )
    status: Mapped[UserStatus] = mapped_column(
        Enum(UserStatus, name="user_status", create_type=False),
        default=UserStatus.PENDING_VERIFICATION,
        nullable=False,
    )
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # Security
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_login_ip: Mapped[str | None] = mapped_column(String(45))

    # Reading Goals
    daily_reading_goal_minutes: Mapped[int | None] = mapped_column(Integer)
    weekly_reading_goal_minutes: Mapped[int | None] = mapped_column(Integer)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Relationships
    oauth_accounts: Mapped[list["OAuthAccount"]] = relationship(
        "OAuthAccount",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    sessions: Mapped[list["UserSession"]] = relationship(
        "UserSession",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    books: Mapped[list["UserBook"]] = relationship(
        "UserBook",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    reading_progress: Mapped[list["ReadingProgress"]] = relationship(
        "ReadingProgress",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    highlights: Mapped[list["Highlight"]] = relationship(
        "Highlight",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    notes: Mapped[list["Note"]] = relationship(
        "Note",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    bookmarks: Mapped[list["Bookmark"]] = relationship(
        "Bookmark",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    reviews: Mapped[list["Review"]] = relationship(
        "Review",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    comments: Mapped[list["Comment"]] = relationship(
        "Comment",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    shelves: Mapped[list["Shelf"]] = relationship(
        "Shelf",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    collections: Mapped[list["Collection"]] = relationship(
        "Collection",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    following: Mapped[list["Follow"]] = relationship(
        "Follow",
        foreign_keys="Follow.follower_id",
        back_populates="follower",
        cascade="all, delete-orphan",
    )
    followers: Mapped[list["Follow"]] = relationship(
        "Follow",
        foreign_keys="Follow.following_id",
        back_populates="following",
        cascade="all, delete-orphan",
    )
    notifications: Mapped[list["Notification"]] = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    reading_sessions: Mapped[list["ReadingSession"]] = relationship(
        "ReadingSession",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    @property
    def is_active(self) -> bool:
        """Check if user account is active."""
        return self.status == UserStatus.ACTIVE and self.deleted_at is None

    @property
    def is_admin(self) -> bool:
        """Check if user is an admin."""
        return self.role == UserRole.ADMIN

    @property
    def is_moderator(self) -> bool:
        """Check if user is a moderator or admin."""
        return self.role in (UserRole.MODERATOR, UserRole.ADMIN)

    @property
    def full_name(self) -> str:
        """Get user's display name or username."""
        return self.display_name or self.username

    @property
    def follower_count(self) -> int:
        """Get number of followers."""
        return len(self.followers) if self.followers else 0

    @property
    def following_count(self) -> int:
        """Get number of users following."""
        return len(self.following) if self.following else 0


class OAuthAccount(Base):
    """OAuth provider account linkage."""

    __tablename__ = "oauth_accounts"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    provider_account_id: Mapped[str] = mapped_column(String(255), nullable=False)
    provider_data: Mapped[dict | None] = mapped_column(JSON)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="oauth_accounts")

    __table_args__ = (
        # Unique constraint on provider + account_id
        {"comment": "OAuth account linkages"},
    )


class UserSession(Base):
    """Active user sessions for device tracking."""

    __tablename__ = "user_sessions"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    refresh_token_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    device_info: Mapped[str | None] = mapped_column(String(255))
    ip_address: Mapped[str | None] = mapped_column(String(45))
    user_agent: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    last_used_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="sessions")
