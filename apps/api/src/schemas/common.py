"""
Common/shared schemas.
"""

from datetime import datetime
from typing import Any, Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict


T = TypeVar("T")


class PaginationParams(BaseModel):
    """Pagination parameters."""
    page: int = 1
    page_size: int = 20


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response."""
    items: list[T]
    total: int
    page: int
    page_size: int
    pages: int
    has_next: bool
    has_prev: bool


class MessageResponse(BaseModel):
    """Simple message response."""
    message: str
    code: str | None = None


class ErrorResponse(BaseModel):
    """Error response."""
    message: str
    code: str
    details: dict[str, Any] | None = None


class UserMiniResponse(BaseModel):
    """Minimal user info for embedding."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str
    display_name: str | None
    avatar_url: str | None


class SearchSuggestion(BaseModel):
    """Search suggestion."""
    type: str  # book, author, category
    id: UUID
    title: str
    subtitle: str | None = None
    cover_url: str | None = None
