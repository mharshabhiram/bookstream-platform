"""
Notification system for in-app and email notifications.
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    String,
    Text,
    func,
    JSON,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.session import Base

if TYPE_CHECKING:
    from src.models.user import User


class NotificationType(str):
    """Notification type constants."""
    BOOK_COMPLETED = "book_completed"
    READING_REMINDER = "reading_reminder"
    GOAL_ACHIEVED = "goal_achieved"
    NEW_FOLLOWER = "new_follower"
    NEW_REVIEW = "new_review"
    NEW_COMMENT = "new_comment"
    HIGHLIGHT_LIKED = "highlight_liked"
    BOOK_RECOMMENDATION = "book_recommendation"
    SYSTEM = "system"


class Notification(Base):
    """User notification model."""

    __tablename__ = "notifications"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Content
    type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str | None] = mapped_column(Text)

    # Action link
    action_url: Mapped[str | None] = mapped_column(String(500))
    action_text: Mapped[str | None] = mapped_column(String(100))

    # Related entities
    related_entity_type: Mapped[str | None] = mapped_column(String(50))
    related_entity_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True))

    # Actor (who triggered the notification)
    actor_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
    )
    actor_name: Mapped[str | None] = mapped_column(String(100))
    actor_avatar: Mapped[str | None] = mapped_column(String(500))

    # Status
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Delivery
    email_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    email_sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    push_sent: Mapped[bool] = mapped_column(Boolean, default=False)

    # Metadata
    metadata: Mapped[dict | None] = mapped_column(JSON)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="notifications",
    )
    actor: Mapped["User"] = relationship(
        "User",
        foreign_keys=[actor_id],
    )

    __table_args__ = (
        Index("ix_notifications_user_unread", "user_id", "is_read", "created_at"),
        Index("ix_notifications_type", "type", "created_at"),
    )


class NotificationPreference(Base):
    """User notification preferences."""

    __tablename__ = "notification_preferences"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    # Email preferences
    email_reading_reminders: Mapped[bool] = mapped_column(Boolean, default=True)
    email_goal_achieved: Mapped[bool] = mapped_column(Boolean, default=True)
    email_social_activity: Mapped[bool] = mapped_column(Boolean, default=True)
    email_recommendations: Mapped[bool] = mapped_column(Boolean, default=True)
    email_newsletter: Mapped[bool] = mapped_column(Boolean, default=True)

    # Push preferences
    push_reading_reminders: Mapped[bool] = mapped_column(Boolean, default=True)
    push_social_activity: Mapped[bool] = mapped_column(Boolean, default=True)
    push_goal_achieved: Mapped[bool] = mapped_column(Boolean, default=True)

    # In-app preferences
    in_app_social: Mapped[bool] = mapped_column(Boolean, default=True)
    in_app_recommendations: Mapped[bool] = mapped_column(Boolean, default=True)

    # Reminder schedule
    reading_reminder_time: Mapped[str | None] = mapped_column(String(5))  # HH:MM format
    reading_reminder_days: Mapped[list[str] | None] = mapped_column(JSON)  # ["mon", "tue", ...]

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
