"""
Social features: reviews, comments, follows, likes.
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
    Float,
    func,
    Index,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.session import Base

if TYPE_CHECKING:
    from src.models.user import User
    from src.models.book import Book


class Review(Base):
    """Book reviews with ratings."""

    __tablename__ = "reviews"

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

    # Rating (1-5 stars)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)

    # Content
    title: Mapped[str | None] = mapped_column(String(255))
    content: Mapped[str | None] = mapped_column(Text)

    # Spoiler handling
    contains_spoilers: Mapped[bool] = mapped_column(Boolean, default=False)

    # Engagement
    helpful_count: Mapped[int] = mapped_column(Integer, default=0)
    not_helpful_count: Mapped[int] = mapped_column(Integer, default=0)

    # Status
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    is_edited: Mapped[bool] = mapped_column(Boolean, default=False)

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
    user: Mapped["User"] = relationship("User", back_populates="reviews")
    book: Mapped["Book"] = relationship("Book", back_populates="reviews")
    comments: Mapped[list["Comment"]] = relationship(
        "Comment",
        back_populates="review",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint("user_id", "book_id", name="uq_reviews_user_book"),
        Index("ix_reviews_book_rating", "book_id", "rating"),
        Index("ix_reviews_recent", "book_id", "created_at"),
    )


class Comment(Base):
    """Comments on reviews or books."""

    __tablename__ = "comments"

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
    review_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("reviews.id", ondelete="CASCADE"),
    )
    parent_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("comments.id", ondelete="CASCADE"),
    )

    # Content
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Engagement
    likes_count: Mapped[int] = mapped_column(Integer, default=0)

    # Status
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    is_edited: Mapped[bool] = mapped_column(Boolean, default=False)

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
    user: Mapped["User"] = relationship("User", back_populates="comments")
    book: Mapped["Book"] = relationship("Book", back_populates="comments")
    review: Mapped["Review"] = relationship("Review", back_populates="comments")
    parent: Mapped["Comment"] = relationship("Comment", remote_side=[id])
    replies: Mapped[list["Comment"]] = relationship("Comment", back_populates="parent")

    __table_args__ = (
        Index("ix_comments_book", "book_id", "created_at"),
        Index("ix_comments_review", "review_id", "created_at"),
    )


class Follow(Base):
    """User follow relationships."""

    __tablename__ = "follows"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    follower_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    following_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Notification preferences
    notify_new_books: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_reviews: Mapped[bool] = mapped_column(Boolean, default=False)
    notify_highlights: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # Relationships
    follower: Mapped["User"] = relationship(
        "User",
        foreign_keys=[follower_id],
        back_populates="following",
    )
    following: Mapped["User"] = relationship(
        "User",
        foreign_keys=[following_id],
        back_populates="followers",
    )

    __table_args__ = (
        UniqueConstraint("follower_id", "following_id", name="uq_follows_pair"),
        Index("ix_follows_follower", "follower_id", "created_at"),
        Index("ix_follows_following", "following_id", "created_at"),
    )


class Like(Base):
    """Generic like model for highlights and comments."""

    __tablename__ = "likes"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Polymorphic like target
    target_type: Mapped[str] = mapped_column(String(50), nullable=False)  # highlight, comment, review
    target_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id", "target_type", "target_id",
            name="uq_likes_user_target",
        ),
        Index("ix_likes_target", "target_type", "target_id"),
    )
