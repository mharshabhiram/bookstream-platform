"""
Custom exception classes for BookStream.
"""

from typing import Any

from fastapi import HTTPException, status


class BookStreamException(Exception):
    """Base exception for the application."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(BookStreamException):
    """Raised when authentication fails."""
    pass


class AuthorizationError(BookStreamException):
    """Raised when user lacks permissions."""
    pass


class ResourceNotFoundError(BookStreamException):
    """Raised when a requested resource is not found."""
    pass


class ValidationError(BookStreamException):
    """Raised when validation fails."""
    pass


class RateLimitError(BookStreamException):
    """Raised when rate limit is exceeded."""
    pass


class StorageError(BookStreamException):
    """Raised when storage operation fails."""
    pass


class EbookProcessingError(BookStreamException):
    """Raised when ebook processing fails."""
    pass


# HTTP Exception mappings
class APIException(HTTPException):
    """HTTP exception with structured error response."""

    def __init__(
        self,
        status_code: int,
        message: str,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            status_code=status_code,
            detail={
                "message": message,
                "code": error_code or f"ERR_{status_code}",
                "details": details or {},
            },
        )


class NotFoundException(APIException):
    def __init__(self, resource: str, identifier: str | None = None):
        message = f"{resource} not found"
        if identifier:
            message += f" with identifier: {identifier}"
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=message,
            error_code="ERR_NOT_FOUND",
        )


class ConflictException(APIException):
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            message=message,
            error_code="ERR_CONFLICT",
        )


class UnauthorizedException(APIException):
    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message=message,
            error_code="ERR_UNAUTHORIZED",
        )


class ForbiddenException(APIException):
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            message=message,
            error_code="ERR_FORBIDDEN",
        )


class BadRequestException(APIException):
    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=message,
            error_code="ERR_BAD_REQUEST",
            details=details,
        )


class TooManyRequestsException(APIException):
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            message=message,
            error_code="ERR_RATE_LIMIT",
        )
