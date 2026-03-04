from __future__ import annotations

from typing import Any, Optional


class AuthoraError(Exception):
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
    def __init__(self, message: str, details: Any = None) -> None:
        super().__init__(message, status_code=0, code="NETWORK_ERROR", details=details)


class TimeoutError(AuthoraError):
    def __init__(self, message: str = "Request timed out") -> None:
        super().__init__(message, status_code=408, code="TIMEOUT")


class AuthenticationError(AuthoraError):
    def __init__(self, message: str = "Authentication failed", details: Any = None) -> None:
        super().__init__(message, status_code=401, code="AUTHENTICATION_ERROR", details=details)


class AuthorizationError(AuthoraError):
    def __init__(self, message: str = "Forbidden", details: Any = None) -> None:
        super().__init__(message, status_code=403, code="AUTHORIZATION_ERROR", details=details)


class NotFoundError(AuthoraError):
    def __init__(self, message: str = "Resource not found", details: Any = None) -> None:
        super().__init__(message, status_code=404, code="NOT_FOUND", details=details)


class ValidationError(AuthoraError):
    def __init__(self, message: str = "Validation failed", details: Any = None) -> None:
        super().__init__(message, status_code=422, code="VALIDATION_ERROR", details=details)


class RateLimitError(AuthoraError):
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        details: Any = None,
    ) -> None:
        super().__init__(message, status_code=429, code="RATE_LIMIT", details=details)
        self.retry_after = retry_after
