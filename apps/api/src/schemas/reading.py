"""
Reading progress, highlights, bookmarks, notes schemas.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ReadingProgressBase(BaseModel):
    """Base reading progress schema."""
    model_config = ConfigDict(from_attributes=True)

    current_cfi: str | None = None
    current_page: int | None = None
    total_pages: int | None = None
    progress_percent: float = Field(0.0, ge=0.0, le=100.0)
    current_chapter_id: str | None = None
    current_chapter_title: str | None = None


class ReadingProgressUpdate(ReadingProgressBase):
    """Update reading progress."""
    time_spent_seconds: int = 0


class ReadingProgressResponse(ReadingProgressBase):
    """Reading progress response."""
    id: UUID
    book_id: UUID
    time_spent_seconds: int
    sessions_count: int
    last_device: str | None
    started_at: datetime | None
    completed_at: datetime | None
    last_read_at: datetime


class HighlightBase(BaseModel):
    """Base highlight schema."""
    model_config = ConfigDict(from_attributes=True)

    start_cfi: str
    end_cfi: str
    start_offset: int = 0
    end_offset: int = 0
    text: str
    chapter_id: str | None = None
    chapter_title: str | None = None
    page_number: int | None = None
    color: str = "yellow"
    style: str = "background"
    note: str | None = None
    is_public: bool = False


class HighlightCreate(HighlightBase):
    """Create highlight."""
    book_id: UUID


class HighlightUpdate(BaseModel):
    """Update highlight."""
    color: str | None = None
    style: str | None = None
    note: str | None = None
    is_public: bool | None = None


class HighlightResponse(HighlightBase):
    """Highlight response."""
    id: UUID
    book_id: UUID
    user_id: UUID
    likes_count: int
    created_at: datetime
    updated_at: datetime


class BookmarkBase(BaseModel):
    """Base bookmark schema."""
    model_config = ConfigDict(from_attributes=True)

    cfi: str
    page_number: int | None = None
    chapter_id: str | None = None
    chapter_title: str | None = None
    text_preview: str | None = None
    label: str | None = Field(None, max_length=100)
    color: str = "blue"


class BookmarkCreate(BookmarkBase):
    """Create bookmark."""
    book_id: UUID


class BookmarkUpdate(BaseModel):
    """Update bookmark."""
    label: str | None = Field(None, max_length=100)
    color: str | None = None


class BookmarkResponse(BookmarkBase):
    """Bookmark response."""
    id: UUID
    book_id: UUID
    user_id: UUID
    created_at: datetime


class NoteBase(BaseModel):
    """Base note schema."""
    model_config = ConfigDict(from_attributes=True)

    cfi: str | None = None
    page_number: int | None = None
    chapter_id: str | None = None
    chapter_title: str | None = None
    title: str | None = Field(None, max_length=255)
    content: str
    tags: list[str] | None = None
    color: str = "white"
    is_public: bool = False


class NoteCreate(NoteBase):
    """Create note."""
    book_id: UUID


class NoteUpdate(BaseModel):
    """Update note."""
    title: str | None = Field(None, max_length=255)
    content: str | None = None
    tags: list[str] | None = None
    color: str | None = None
    is_public: bool | None = None


class NoteResponse(NoteBase):
    """Note response."""
    id: UUID
    book_id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
