"""
Book Pydantic schemas.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class AuthorBase(BaseModel):
    """Base author schema."""
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., min_length=1, max_length=255)
    bio: str | None = None
    avatar_url: str | None = None


class AuthorResponse(AuthorBase):
    """Author response."""
    id: UUID
    slug: str
    created_at: datetime


class CategoryBase(BaseModel):
    """Base category schema."""
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    icon: str | None = None
    color: str | None = None


class CategoryResponse(CategoryBase):
    """Category response."""
    id: UUID
    slug: str
    parent_id: UUID | None
    is_featured: bool
    books_count: int = 0


class BookBase(BaseModel):
    """Base book schema."""
    model_config = ConfigDict(from_attributes=True)

    title: str = Field(..., min_length=1, max_length=500)
    subtitle: str | None = Field(None, max_length=500)
    description: str | None = None
    author_name: str | None = Field(None, max_length=255)
    isbn: str | None = Field(None, max_length=20)
    language: str = "en"
    page_count: int | None = None
    published_date: datetime | None = None
    publisher: str | None = None


class BookCreate(BookBase):
    """Book creation schema (metadata only)."""
    category_ids: list[UUID] = []


class BookResponse(BookBase):
    """Book response schema."""
    id: UUID
    slug: str
    cover_url: str | None
    cover_blurhash: str | None
    thumbnail_url: str | None
    file_format: str
    file_size: int
    average_rating: float
    total_reviews: int
    total_reads: int
    is_public: bool
    is_featured: bool
    is_processed: bool
    author: AuthorResponse | None
    categories: list[CategoryResponse]
    created_at: datetime
    updated_at: datetime


class BookDetailResponse(BookResponse):
    """Detailed book response."""
    toc: list[dict] | None
    metadata: dict | None
    user_book: "UserBookResponse | None" = None


class BookListResponse(BaseModel):
    """Paginated book list response."""
    items: list[BookResponse]
    total: int
    page: int
    page_size: int
    pages: int


class BookUploadResponse(BaseModel):
    """Book upload response."""
    id: UUID
    title: str
    status: str  # processing, completed, failed
    message: str | None = None


class UserBookBase(BaseModel):
    """Base user book schema."""
    model_config = ConfigDict(from_attributes=True)

    is_favorite: bool = False
    is_archived: bool = False
    status: str = "unread"
    user_rating: int | None = Field(None, ge=1, le=5)
    user_notes: str | None = None


class UserBookUpdate(BaseModel):
    """Update user book."""
    is_favorite: bool | None = None
    is_archived: bool | None = None
    status: str | None = Field(None, pattern=r"^(unread|reading|completed)$")
    user_rating: int | None = Field(None, ge=1, le=5)
    user_notes: str | None = None


class UserBookResponse(UserBookBase):
    """User book response."""
    id: UUID
    book_id: UUID
    last_read_at: datetime | None
    last_position: str | None
    last_progress_percent: float
    created_at: datetime
    book: BookResponse


class BookSearchFilters(BaseModel):
    """Book search filters."""
    query: str | None = None
    category_id: UUID | None = None
    author_id: UUID | None = None
    format: str | None = Field(None, pattern=r"^(epub|pdf|mobi|azw3|txt)$")
    language: str | None = None
    min_rating: float | None = Field(None, ge=0, le=5)
    year_from: int | None = None
    year_to: int | None = None
    sort_by: str = "created_at"
    sort_order: str = "desc"
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
