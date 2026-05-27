"""
Library organization: shelves and collections.
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
    JSON,
    Index,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.session import Base

if TYPE_CHECKING:
    from src.models.user import User
    from src.models.book import Book


class Shelf(Base):
    """User-created bookshelves (e.g., 'To Read', 'Favorites')."""

    __tablename__ = "shelves"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Info
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    color: Mapped[str | None] = mapped_column(String(7))  # Hex color
    icon: Mapped[str | None] = mapped_column(String(50))

    # Organization
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)

    # Stats
    books_count: Mapped[int] = mapped_column(Integer, default=0)

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
    user: Mapped["User"] = relationship("User", back_populates="shelves")
    books: Mapped[list["ShelfBook"]] = relationship(
        "ShelfBook",
        back_populates="shelf",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint("user_id", "slug", name="uq_shelves_user_slug"),
        Index("ix_shelves_user", "user_id", "sort_order"),
    )


class ShelfBook(Base):
    """Many-to-many relationship between shelves and books."""

    __tablename__ = "shelf_books"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    shelf_id: Mapped[UUID] = mapped_column(
        ForeignKey("shelves.id", ondelete="CASCADE"),
        nullable=False,
    )
    book_id: Mapped[UUID] = mapped_column(
        ForeignKey("books.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Organization within shelf
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    added_note: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # Relationships
    shelf: Mapped["Shelf"] = relationship("Shelf", back_populates="books")
    book: Mapped["Book"] = relationship("Book")

    __table_args__ = (
        UniqueConstraint("shelf_id", "book_id", name="uq_shelf_books_pair"),
    )


class Collection(Base):
    """Curated book collections (public reading lists)."""

    __tablename__ = "collections"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Info
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    cover_url: Mapped[str | None] = mapped_column(String(500))

    # Organization
    tags: Mapped[list[str] | None] = mapped_column(JSON)

    # Visibility
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)

    # Stats
    books_count: Mapped[int] = mapped_column(Integer, default=0)
    followers_count: Mapped[int] = mapped_column(Integer, default=0)
    views_count: Mapped[int] = mapped_column(Integer, default=0)

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
    user: Mapped["User"] = relationship("User", back_populates="collections")
    books: Mapped[list["CollectionBook"]] = relationship(
        "CollectionBook",
        back_populates="collection",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint("user_id", "slug", name="uq_collections_user_slug"),
        Index("ix_collections_featured", "is_featured", "is_public"),
        Index("ix_collections_user", "user_id", "created_at"),
    )


class CollectionBook(Base):
    """Books within a collection with ordering."""

    __tablename__ = "collection_books"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    collection_id: Mapped[UUID] = mapped_column(
        ForeignKey("collections.id", ondelete="CASCADE"),
        nullable=False,
    )
    book_id: Mapped[UUID] = mapped_column(
        ForeignKey("books.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Organization
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    added_note: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # Relationships
    collection: Mapped["Collection"] = relationship("Collection", back_populates="books")
    book: Mapped["Book"] = relationship("Book")

    __table_args__ = (
        UniqueConstraint("collection_id", "book_id", name="uq_collection_books_pair"),
    )
