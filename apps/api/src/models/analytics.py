"""
Reading analytics and engagement tracking.
"""

from datetime import datetime, date
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Float,
    func,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.session import Base

if TYPE_CHECKING:
    from src.models.user import User
    from src.models.book import Book


class ReadingSession(Base):
    """Individual reading sessions for detailed analytics."""

    __tablename__ = "reading_sessions"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    book_id: Mapped[UUID] = mapped_column(
        ForeignKey("books.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Session metrics
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0)
    pages_read: Mapped[int | None] = mapped_column(Integer)

    # Progress
    start_progress: Mapped[float] = mapped_column(Float, default=0.0)
    end_progress: Mapped[float] = mapped_column(Float, default=0.0)

    # Device
    device_type: Mapped[str | None] = mapped_column()  # mobile, tablet, desktop

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="reading_sessions")
    book: Mapped["Book"] = relationship("Book")

    __table_args__ = (
        Index("ix_reading_sessions_user_date", "user_id", "started_at"),
        Index("ix_reading_sessions_book", "book_id", "started_at"),
    )


class DailyReadingStats(Base):
    """Aggregated daily reading statistics per user."""

    __tablename__ = "daily_reading_stats"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)

    # Stats
    total_minutes: Mapped[int] = mapped_column(Integer, default=0)
    sessions_count: Mapped[int] = mapped_column(Integer, default=0)
    books_started: Mapped[int] = mapped_column(Integer, default=0)
    books_completed: Mapped[int] = mapped_column(Integer, default=0)
    pages_read: Mapped[int] = mapped_column(Integer, default=0)

    # Streak
    streak_day: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        Index("ix_daily_stats_user_date", "user_id", "date", unique=True),
    )


class BookAnalytics(Base):
    """Aggregated book-level analytics."""

    __tablename__ = "book_analytics"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    book_id: Mapped[UUID] = mapped_column(
        ForeignKey("books.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    # Engagement
    total_readers: Mapped[int] = mapped_column(Integer, default=0)
    active_readers: Mapped[int] = mapped_column(Integer, default=0)
    completions: Mapped[int] = mapped_column(Integer, default=0)

    # Time
    total_reading_minutes: Mapped[int] = mapped_column(Integer, default=0)
    avg_completion_time_minutes: Mapped[int | None] = mapped_column(Integer)

    # Drop-off analysis
    avg_progress_percent: Mapped[float] = mapped_column(Float, default=0.0)

    # Social
    total_highlights: Mapped[int] = mapped_column(Integer, default=0)
    total_notes: Mapped[int] = mapped_column(Integer, default=0)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
