"""
Email service for notifications and transactional emails.
"""

from typing import Any

import aiosmtplib
from jinja2 import Environment, PackageLoader

from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)


class EmailService:
    """Async email service with Jinja2 templates."""

    def __init__(self):
        self._jinja = Environment(
            loader=PackageLoader("src", "templates/emails"),
            autoescape=True,
        )
        self._enabled = all([
            settings.SMTP_USER,
            settings.SMTP_PASSWORD,
        ])

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str | None = None,
    ) -> None:
        """Send an email."""
        if not self._enabled:
            logger.info("email_skipped", to=to_email, subject=subject)
            return

        message = f"""From: {settings.SMTP_FROM}
To: {to_email}
Subject: {subject}
MIME-Version: 1.0
Content-Type: multipart/alternative; boundary="boundary"

--boundary
Content-Type: text/plain; charset="utf-8"

{text_content or ""}

--boundary
Content-Type: text/html; charset="utf-8"

{html_content}

--boundary--"""

        try:
            await aiosmtplib.send(
                message,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USER,
                password=settings.SMTP_PASSWORD,
                start_tls=settings.SMTP_TLS,
            )
            logger.info("email_sent", to=to_email, subject=subject)
        except Exception as e:
            logger.error("email_send_failed", to=to_email, error=str(e))

    async def send_verification_email(
        self,
        to_email: str,
        username: str,
        verification_url: str,
    ) -> None:
        """Send email verification email."""
        subject = f"Verify your email - {settings.APP_NAME}"
        html = self._jinja.get_template("verify_email.html").render(
            app_name=settings.APP_NAME,
            username=username,
            verification_url=verification_url,
        )
        await self.send_email(to_email, subject, html)

    async def send_password_reset(
        self,
        to_email: str,
        username: str,
        reset_url: str,
    ) -> None:
        """Send password reset email."""
        subject = f"Password reset - {settings.APP_NAME}"
        html = self._jinja.get_template("password_reset.html").render(
            app_name=settings.APP_NAME,
            username=username,
            reset_url=reset_url,
        )
        await self.send_email(to_email, subject, html)

    async def send_welcome_email(
        self,
        to_email: str,
        username: str,
    ) -> None:
        """Send welcome email."""
        subject = f"Welcome to {settings.APP_NAME}!"
        html = self._jinja.get_template("welcome.html").render(
            app_name=settings.APP_NAME,
            username=username,
            app_url=settings.APP_URL,
        )
        await self.send_email(to_email, subject, html)


# Singleton
email_service = EmailService()
