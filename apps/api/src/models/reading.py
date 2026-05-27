"""
Reading progress, highlights, bookmarks, and notes models.
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    Float,
    func,
    JSON,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.session import Base

if TYPE_CHECKING:
    from src.models.user import User
    from src.models.book import Book


class ReadingProgress(Base):
    """Tracks user's reading progress in a book."""

    __tablename__ = "reading_progress"

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

    # Position tracking
    current_cfi: Mapped[str | None] = mapped_column(String(255))
    current_page: Mapped[int | None] = mapped_column(Integer)
    total_pages: Mapped[int | None] = mapped_column(Integer)
    progress_percent: Mapped[float] = mapped_column(Float, default=0.0)

    # Chapter info
    current_chapter_id: Mapped[str | None] = mapped_column(String(255))
    current_chapter_title: Mapped[str | None] = mapped_column(String(500))

    # Reading session
    time_spent_seconds: Mapped[int] = mapped_column(Integer, default=0)
    sessions_count: Mapped[int] = mapped_column(Integer, default=0)

    # Device sync
    last_device: Mapped[str | None] = mapped_column(String(255))

    # Timestamps
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_read_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="reading_progress")
    book: Mapped["Book"] = relationship("Book", back_populates="reading_progress")

    __table_args__ = (
        Index("ix_reading_progress_user_book", "user_id", "book_id", unique=True),
        Index("ix_reading_progress_recent", "user_id", "last_read_at"),
    )


class HighlightColor(str):
    """Highlight color options."""
    YELLOW = "yellow"
    GREEN = "green"
    BLUE = "blue"
    PINK = "pink"
    PURPLE = "purple"
    ORANGE = "orange"


class Highlight(Base):
    """User text highlights in books."""

    __tablename__ = "highlights"

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

    # Location
    start_cfi: Mapped[str] = mapped_column(String(255), nullable=False)
    end_cfi: Mapped[str] = mapped_column(String(255), nullable=False)
    start_offset: Mapped[int] = mapped_column(Integer, default=0)
    end_offset: Mapped[int] = mapped_column(Integer, default=0)

    # Content
    text: Mapped[str] = mapped_column(Text, nullable=False)
    chapter_id: Mapped[str | None] = mapped_column(String(255))
    chapter_title: Mapped[str | None] = mapped_column(String(500))
    page_number: Mapped[int | None] = mapped_column(Integer)

    # Styling
    color: Mapped[str] = mapped_column(String(20), default="yellow")
    style: Mapped[str] = mapped_column(String(20), default="background")  # background, underline, squiggly

    # Note attached to highlight
    note: Mapped[str | None] = mapped_column(Text)

    # Social
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    likes_count: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="highlights")
    book: Mapped["Book"] = relationship("Book", back_populates="highlights")

    __table_args__ = (
        Index("ix_highlights_user_book", "user_id", "book_id"),
        Index("ix_highlights_chapter", "book_id", "chapter_id"),
    )


class Bookmark(Base):
    """User bookmarks in books."""

    __tablename__ = "bookmarks"

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

    # Location
    cfi: Mapped[str] = mapped_column(String(255), nullable=False)
    page_number: Mapped[int | None] = mapped_column(Integer)
    chapter_id: Mapped[str | None] = mapped_column(String(255))
    chapter_title: Mapped[str | None] = mapped_column(String(500))

    # Content preview
    text_preview: Mapped[str | None] = mapped_column(Text)

    # Organization
    label: Mapped[str | None] = mapped_column(String(100))
    color: Mapped[str] = mapped_column(String(20), default="blue")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="bookmarks")
    book: Mapped["Book"] = relationship("Book", back_populates="bookmarks")

    __table_args__ = (
        Index("ix_bookmarks_user_book", "user_id", "book_id"),
    )


class Note(Base):
    """User notes attached to book locations."""

    __tablename__ = "notes"

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

    # Location (optional - can be general book note)
    cfi: Mapped[str | None] = mapped_column(String(255))
    page_number: Mapped[int | None] = mapped_column(Integer)
    chapter_id: Mapped[str | None] = mapped_column(String(255))
    chapter_title: Mapped[str | None] = mapped_column(String(500))

    # Content
    title: Mapped[str | None] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Organization
    tags: Mapped[list[str] | None] = mapped_column(JSON)
    color: Mapped[str] = mapped_column(String(20), default="white")

    # Social
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="notes")
    book: Mapped["Book"] = relationship("Book", back_populates="notes")

    __table_args__ = (
        Index("ix_notes_user_book", "user_id", "book_id"),
    )
