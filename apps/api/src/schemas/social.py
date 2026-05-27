"""
Social feature schemas.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ReviewBase(BaseModel):
    """Base review schema."""
    model_config = ConfigDict(from_attributes=True)

    rating: int = Field(..., ge=1, le=5)
    title: str | None = Field(None, max_length=255)
    content: str | None = None
    contains_spoilers: bool = False


class ReviewCreate(ReviewBase):
    """Create review."""
    book_id: UUID


class ReviewUpdate(BaseModel):
    """Update review."""
    rating: int | None = Field(None, ge=1, le=5)
    title: str | None = Field(None, max_length=255)
    content: str | None = None
    contains_spoilers: bool | None = None


class ReviewResponse(ReviewBase):
    """Review response."""
    id: UUID
    book_id: UUID
    user_id: UUID
    user: "UserMiniResponse"
    helpful_count: int
    not_helpful_count: int
    is_public: bool
    is_edited: bool
    created_at: datetime
    updated_at: datetime


class CommentBase(BaseModel):
    """Base comment schema."""
    model_config = ConfigDict(from_attributes=True)

    content: str = Field(..., min_length=1, max_length=5000)


class CommentCreate(CommentBase):
    """Create comment."""
    book_id: UUID
    review_id: UUID | None = None
    parent_id: UUID | None = None


class CommentUpdate(BaseModel):
    """Update comment."""
    content: str | None = Field(None, min_length=1, max_length=5000)


class CommentResponse(CommentBase):
    """Comment response."""
    id: UUID
    book_id: UUID
    user_id: UUID
    user: "UserMiniResponse"
    review_id: UUID | None
    parent_id: UUID | None
    likes_count: int
    is_public: bool
    is_edited: bool
    replies: list["CommentResponse"] = []
    created_at: datetime
    updated_at: datetime


class FollowResponse(BaseModel):
    """Follow relationship response."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    follower_id: UUID
    following_id: UUID
    follower: "UserMiniResponse"
    following: "UserMiniResponse"
    created_at: datetime


class LikeResponse(BaseModel):
    """Like response."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    target_type: str
    target_id: UUID
    created_at: datetime
