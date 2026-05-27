"""
Notification schemas.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class NotificationResponse(BaseModel):
    """Notification response."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    type: str
    title: str
    message: str | None
    action_url: str | None
    action_text: str | None
    related_entity_type: str | None
    related_entity_id: UUID | None
    actor_id: UUID | None
    actor_name: str | None
    actor_avatar: str | None
    is_read: bool
    read_at: datetime | None
    created_at: datetime


class NotificationPreferenceResponse(BaseModel):
    """Notification preferences response."""
    model_config = ConfigDict(from_attributes=True)

    email_reading_reminders: bool
    email_goal_achieved: bool
    email_social_activity: bool
    email_recommendations: bool
    email_newsletter: bool
    push_reading_reminders: bool
    push_social_activity: bool
    push_goal_achieved: bool
    in_app_social: bool
    in_app_recommendations: bool
    reading_reminder_time: str | None
    reading_reminder_days: list[str] | None


class NotificationPreferenceUpdate(BaseModel):
    """Update notification preferences."""
    email_reading_reminders: bool | None = None
    email_goal_achieved: bool | None = None
    email_social_activity: bool | None = None
    email_recommendations: bool | None = None
    email_newsletter: bool | None = None
    push_reading_reminders: bool | None = None
    push_social_activity: bool | None = None
    push_goal_achieved: bool | None = None
    in_app_social: bool | None = None
    in_app_recommendations: bool | None = None
    reading_reminder_time: str | None = None
    reading_reminder_days: list[str] | None = None
