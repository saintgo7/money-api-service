"""Exceptions for Money API SDK."""


class MoneyAPIError(Exception):
    """Base exception for Money API errors."""
    pass


class RateLimitError(MoneyAPIError):
    """Raised when rate limit is exceeded."""

    def __init__(self, message: str, retry_after: int = 0):
        super().__init__(message)
        self.retry_after = retry_after


class InsufficientCreditsError(MoneyAPIError):
    """Raised when account has insufficient credits."""
    pass


class AuthenticationError(MoneyAPIError):
    """Raised on authentication failures."""
    pass


class ValidationError(MoneyAPIError):
    """Raised on validation errors."""
    pass
