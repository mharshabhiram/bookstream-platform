"""
Library organization schemas.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ShelfBase(BaseModel):
    """Base shelf schema."""
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    color: str | None = Field(None, max_length=7)
    icon: str | None = Field(None, max_length=50)
    is_public: bool = False


class ShelfCreate(ShelfBase):
    """Create shelf."""
    pass


class ShelfUpdate(BaseModel):
    """Update shelf."""
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None
    color: str | None = Field(None, max_length=7)
    icon: str | None = Field(None, max_length=50)
    is_public: bool | None = None
    sort_order: int | None = None


class ShelfResponse(ShelfBase):
    """Shelf response."""
    id: UUID
    slug: str
    sort_order: int
    is_default: bool
    books_count: int
    created_at: datetime
    updated_at: datetime


class ShelfBookResponse(BaseModel):
    """Shelf book response."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    shelf_id: UUID
    book_id: UUID
    sort_order: int
    added_note: str | None
    book: "BookResponse"
    created_at: datetime


class CollectionBase(BaseModel):
    """Base collection schema."""
    model_config = ConfigDict(from_attributes=True)

    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    tags: list[str] | None = None
    is_public: bool = True


class CollectionCreate(CollectionBase):
    """Create collection."""
    pass


class CollectionUpdate(BaseModel):
    """Update collection."""
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    tags: list[str] | None = None
    is_public: bool | None = None
    cover_url: str | None = None


class CollectionResponse(CollectionBase):
    """Collection response."""
    id: UUID
    slug: str
    user_id: UUID
    user: "UserMiniResponse"
    cover_url: str | None
    is_featured: bool
    books_count: int
    followers_count: int
    views_count: int
    created_at: datetime
    updated_at: datetime


class CollectionBookResponse(BaseModel):
    """Collection book response."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    collection_id: UUID
    book_id: UUID
    sort_order: int
    added_note: str | None
    book: "BookResponse"
    created_at: datetime
