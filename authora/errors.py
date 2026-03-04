"""Error hierarchy for the Authora SDK.

All errors raised by the SDK inherit from ``AuthoraError`` so callers can
catch a single base class when broad error handling is preferred.
"""

from __future__ import annotations

from typing import Any, Optional


class AuthoraError(Exception):
    """Base error for all Authora SDK errors.

    Attributes:
        message: Human-readable error description.
        status_code: HTTP status code that triggered the error (0 for network errors).
        code: Machine-readable error code returned by the API, if any.
        details: Additional structured error details from the API response.
    """

    def __init__(
        self,
        message: str,
        status_code: int = 0,
        code: Optional[str] = None,
        details: Any = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code
        self.details = details

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(message={self.message!r}, "
            f"status_code={self.status_code}, code={self.code!r})"
        )


class NetworkError(AuthoraError):
    """Raised when an API request fails due to a network or connectivity issue."""

    def __init__(self, message: str, details: Any = None) -> None:
        super().__init__(message, status_code=0, code="NETWORK_ERROR", details=details)


class TimeoutError(AuthoraError):
    """Raised when the request exceeds the configured timeout."""

    def __init__(self, message: str = "Request timed out") -> None:
        super().__init__(message, status_code=408, code="TIMEOUT")


class AuthenticationError(AuthoraError):
    """Raised when authentication fails (HTTP 401)."""

    def __init__(self, message: str = "Authentication failed", details: Any = None) -> None:
        super().__init__(message, status_code=401, code="AUTHENTICATION_ERROR", details=details)


class AuthorizationError(AuthoraError):
    """Raised when authorization fails (HTTP 403)."""

    def __init__(self, message: str = "Forbidden", details: Any = None) -> None:
        super().__init__(message, status_code=403, code="AUTHORIZATION_ERROR", details=details)


class NotFoundError(AuthoraError):
    """Raised when the requested resource is not found (HTTP 404)."""

    def __init__(self, message: str = "Resource not found", details: Any = None) -> None:
        super().__init__(message, status_code=404, code="NOT_FOUND", details=details)


class ValidationError(AuthoraError):
    """Raised when request validation fails (HTTP 422)."""

    def __init__(self, message: str = "Validation failed", details: Any = None) -> None:
        super().__init__(message, status_code=422, code="VALIDATION_ERROR", details=details)


class RateLimitError(AuthoraError):
    """Raised when the request is rate-limited (HTTP 429).

    Attributes:
        retry_after: Number of seconds to wait before retrying, if provided.
    """

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        details: Any = None,
    ) -> None:
        super().__init__(message, status_code=429, code="RATE_LIMIT", details=details)
        self.retry_after = retry_after
