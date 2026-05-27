"""
Book and Author models with metadata extraction support.
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
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
    from src.models.reading import ReadingProgress, Highlight, Bookmark, Note
    from src.models.social import Review, Comment
    from src.models.library import Shelf, Collection


class Author(Base):
    """Book author model."""

    __tablename__ = "authors"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    bio: Mapped[str | None] = mapped_column(Text)
    avatar_url: Mapped[str | None] = mapped_column(String(500))
    birth_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    death_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # Relationships
    books: Mapped[list["Book"]] = relationship("Book", back_populates="author")


class Category(Base):
    """Book category/genre model."""

    __tablename__ = "categories"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    icon: Mapped[str | None] = mapped_column(String(100))
    color: Mapped[str | None] = mapped_column(String(7))  # Hex color
    parent_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"),
    )
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # Relationships
    parent: Mapped["Category"] = relationship("Category", remote_side=[id])
    children: Mapped[list["Category"]] = relationship("Category", back_populates="parent")
    books: Mapped[list["BookCategory"]] = relationship("BookCategory", back_populates="category")


class Book(Base):
    """Ebook model with metadata and file information."""

    __tablename__ = "books"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Basic Info
    title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(500), unique=True, index=True)
    subtitle: Mapped[str | None] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(Text)

    # Author
    author_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("authors.id", ondelete="SET NULL"),
    )
    author_name: Mapped[str | None] = mapped_column(String(255))

    # Metadata
    isbn: Mapped[str | None] = mapped_column(String(20), index=True)
    isbn13: Mapped[str | None] = mapped_column(String(20), index=True)
    language: Mapped[str] = mapped_column(String(10), default="en")
    page_count: Mapped[int | None] = mapped_column(Integer)
    word_count: Mapped[int | None] = mapped_column(Integer)
    published_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    publisher: Mapped[str | None] = mapped_column(String(255))
    edition: Mapped[str | None] = mapped_column(String(50))

    # File Info
    file_url: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    file_format: Mapped[str] = mapped_column(String(20), nullable=False)  # epub, pdf, mobi, etc.
    file_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    # Cover
    cover_url: Mapped[str | None] = mapped_column(String(500))
    cover_blurhash: Mapped[str | None] = mapped_column(String(100))
    thumbnail_url: Mapped[str | None] = mapped_column(String(500))

    # Content
    toc: Mapped[list[dict] | None] = mapped_column(JSON)  # Table of contents
    metadata: Mapped[dict | None] = mapped_column(JSON)  # Extra metadata from file

    # Stats
    total_reads: Mapped[int] = mapped_column(Integer, default=0)
    total_reviews: Mapped[int] = mapped_column(Integer, default=0)
    average_rating: Mapped[float] = mapped_column(Float, default=0.0)

    # Status
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    is_processed: Mapped[bool] = mapped_column(Boolean, default=False)
    processing_error: Mapped[str | None] = mapped_column(Text)

    # Upload info
    uploaded_by_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
    )

    # Timestamps
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
    author: Mapped["Author"] = relationship("Author", back_populates="books")
    categories: Mapped[list["BookCategory"]] = relationship(
        "BookCategory",
        back_populates="book",
        cascade="all, delete-orphan",
    )
    user_books: Mapped[list["UserBook"]] = relationship(
        "UserBook",
        back_populates="book",
        cascade="all, delete-orphan",
    )
    reading_progress: Mapped[list["ReadingProgress"]] = relationship(
        "ReadingProgress",
        back_populates="book",
        cascade="all, delete-orphan",
    )
    highlights: Mapped[list["Highlight"]] = relationship(
        "Highlight",
        back_populates="book",
        cascade="all, delete-orphan",
    )
    notes: Mapped[list["Note"]] = relationship(
        "Note",
        back_populates="book",
        cascade="all, delete-orphan",
    )
    bookmarks: Mapped[list["Bookmark"]] = relationship(
        "Bookmark",
        back_populates="book",
        cascade="all, delete-orphan",
    )
    reviews: Mapped[list["Review"]] = relationship(
        "Review",
        back_populates="book",
        cascade="all, delete-orphan",
    )
    comments: Mapped[list["Comment"]] = relationship(
        "Comment",
        back_populates="book",
        cascade="all, delete-orphan",
    )

    # Indexes
    __table_args__ = (
        Index("ix_books_search", "title", "author_name"),
        Index("ix_books_featured", "is_featured", "is_public"),
        Index("ix_books_rating", "average_rating", "total_reviews"),
    )


class BookCategory(Base):
    """Many-to-many relationship between books and categories."""

    __tablename__ = "book_categories"

    book_id: Mapped[UUID] = mapped_column(
        ForeignKey("books.id", ondelete="CASCADE"),
        primary_key=True,
    )
    category_id: Mapped[UUID] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"),
        primary_key=True,
    )

    # Relationships
    book: Mapped["Book"] = relationship("Book", back_populates="categories")
    category: Mapped["Category"] = relationship("Category", back_populates="books")


class UserBook(Base):
    """User's personal book library entry."""

    __tablename__ = "user_books"

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

    # Status
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(20), default="unread")  # unread, reading, completed

    # Reading position
    last_read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_position: Mapped[str | None] = mapped_column(String(255))  # CFI or page number
    last_progress_percent: Mapped[float] = mapped_column(Float, default=0.0)

    # User metadata
    user_rating: Mapped[int | None] = mapped_column(Integer)
    user_notes: Mapped[str | None] = mapped_column(Text)

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
    user: Mapped["User"] = relationship("User", back_populates="books")
    book: Mapped["Book"] = relationship("Book", back_populates="user_books")

    __table_args__ = (
        Index("ix_user_books_status", "user_id", "status"),
        Index("ix_user_books_recent", "user_id", "last_read_at"),
    )
