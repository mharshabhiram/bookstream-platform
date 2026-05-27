"""
Analytics schemas.
"""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ReadingStatsResponse(BaseModel):
    """User reading statistics."""
    model_config = ConfigDict(from_attributes=True)

    total_books_read: int
    total_books_reading: int
    total_pages_read: int
    total_reading_time_minutes: int
    average_rating_given: float
    current_streak_days: int
    longest_streak_days: int
    daily_average_minutes: float
    weekly_goal_progress: float
    monthly_books_completed: int


class DailyStatsResponse(BaseModel):
    """Daily reading stats."""
    model_config = ConfigDict(from_attributes=True)

    date: date
    total_minutes: int
    sessions_count: int
    books_started: int
    books_completed: int
    pages_read: int
    streak_day: int


class BookAnalyticsResponse(BaseModel):
    """Book analytics response."""
    model_config = ConfigDict(from_attributes=True)

    book_id: UUID
    total_readers: int
    active_readers: int
    completions: int
    total_reading_minutes: int
    avg_completion_time_minutes: int | None
    avg_progress_percent: float
    total_highlights: int
    total_notes: int
