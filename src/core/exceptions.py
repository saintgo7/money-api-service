"""Custom exception classes for Money API."""
from typing import Optional, Dict, Any


class MoneyAPIException(Exception):
    """Base exception for all Money API errors."""

    def __init__(
        self,
        message: str,
        code: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary."""
        return {
            "error": {
                "message": self.message,
                "code": self.code,
                "status_code": self.status_code,
                "details": self.details
            }
        }


# Authentication Errors
class AuthenticationError(MoneyAPIException):
    """Base authentication error."""

    def __init__(self, message: str = "Authentication failed", details: Optional[Dict] = None):
        super().__init__(
            message=message,
            code="AUTHENTICATION_ERROR",
            status_code=401,
            details=details
        )


class APIKeyInvalid(AuthenticationError):
    """Invalid API key."""

    def __init__(self, message: str = "Invalid API key"):
        super().__init__(
            message=message,
            code="API_KEY_INVALID",
            details={"hint": "Check your API key in the dashboard"}
        )


class APIKeyExpired(AuthenticationError):
    """Expired API key."""

    def __init__(self, message: str = "API key has expired"):
        super().__init__(
            message=message,
            code="API_KEY_EXPIRED",
            details={"hint": "Create a new API key"}
        )


class APIKeyRevoked(AuthenticationError):
    """Revoked API key."""

    def __init__(self, message: str = "API key has been revoked"):
        super().__init__(
            message=message,
            code="API_KEY_REVOKED",
            details={"hint": "This key can no longer be used"}
        )


# Rate Limiting Errors
class RateLimitError(MoneyAPIException):
    """Base rate limit error."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        details: Optional[Dict] = None
    ):
        details = details or {}
        if retry_after:
            details["retry_after"] = retry_after
        super().__init__(
            message=message,
            code="RATE_LIMIT_EXCEEDED",
            status_code=429,
            details=details
        )
        self.retry_after = retry_after


class QuotaExceeded(RateLimitError):
    """Monthly quota exceeded."""

    def __init__(self, message: str = "Monthly quota exceeded"):
        super().__init__(
            message=message,
            code="QUOTA_EXCEEDED",
            details={"hint": "Upgrade your plan or wait for quota reset"}
        )


# Payment Errors
class PaymentError(MoneyAPIException):
    """Base payment error."""

    def __init__(self, message: str = "Payment error", details: Optional[Dict] = None):
        super().__init__(
            message=message,
            code="PAYMENT_ERROR",
            status_code=402,
            details=details
        )


class InsufficientCredits(PaymentError):
    """Insufficient account balance."""

    def __init__(
        self,
        message: str = "Insufficient credits",
        current_balance: Optional[float] = None,
        required: Optional[float] = None
    ):
        details = {}
        if current_balance is not None:
            details["current_balance"] = current_balance
        if required is not None:
            details["required"] = required
        super().__init__(
            message=message,
            code="INSUFFICIENT_CREDITS",
            details=details
        )


class PaymentRequired(PaymentError):
    """Payment required to continue."""

    def __init__(self, message: str = "Payment required"):
        super().__init__(
            message=message,
            code="PAYMENT_REQUIRED",
            details={"hint": "Add credits to your account"}
        )


# Validation Errors
class ValidationError(MoneyAPIException):
    """Base validation error."""

    def __init__(self, message: str = "Validation error", details: Optional[Dict] = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=422,
            details=details
        )


class InvalidParameter(ValidationError):
    """Invalid parameter value."""

    def __init__(self, parameter: str, message: str):
        super().__init__(
            message=message,
            code="INVALID_PARAMETER",
            details={"parameter": parameter}
        )


class MissingParameter(ValidationError):
    """Required parameter missing."""

    def __init__(self, parameter: str):
        super().__init__(
            message=f"Required parameter '{parameter}' is missing",
            code="MISSING_PARAMETER",
            details={"parameter": parameter}
        )


# Resource Errors
class ResourceError(MoneyAPIException):
    """Base resource error."""

    def __init__(self, message: str = "Resource error", details: Optional[Dict] = None):
        super().__init__(
            message=message,
            code="RESOURCE_ERROR",
            status_code=404,
            details=details
        )


class ResourceNotFound(ResourceError):
    """Resource not found."""

    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            message=f"{resource_type} not found",
            code="RESOURCE_NOT_FOUND",
            details={
                "resource_type": resource_type,
                "resource_id": resource_id
            }
        )


class ResourceAlreadyExists(MoneyAPIException):
    """Resource already exists."""

    def __init__(self, resource_type: str, identifier: str):
        super().__init__(
            message=f"{resource_type} already exists",
            code="RESOURCE_ALREADY_EXISTS",
            status_code=409,
            details={
                "resource_type": resource_type,
                "identifier": identifier
            }
        )


# Permission Errors
class PermissionError(MoneyAPIException):
    """Base permission error."""

    def __init__(self, message: str = "Permission denied", details: Optional[Dict] = None):
        super().__init__(
            message=message,
            code="PERMISSION_DENIED",
            status_code=403,
            details=details
        )


class InsufficientPermissions(PermissionError):
    """Insufficient permissions for action."""

    def __init__(self, action: str, required_role: str):
        super().__init__(
            message=f"Insufficient permissions to {action}",
            code="INSUFFICIENT_PERMISSIONS",
            details={
                "action": action,
                "required_role": required_role
            }
        )


# External Service Errors
class ExternalServiceError(MoneyAPIException):
    """Base external service error."""

    def __init__(
        self,
        message: str = "External service error",
        service: str = "unknown",
        details: Optional[Dict] = None
    ):
        details = details or {}
        details["service"] = service
        super().__init__(
            message=message,
            code="EXTERNAL_SERVICE_ERROR",
            status_code=502,
            details=details
        )


class AIProviderError(ExternalServiceError):
    """AI provider error."""

    def __init__(self, provider: str, message: str):
        super().__init__(
            message=f"AI provider error: {message}",
            service=provider,
            code="AI_PROVIDER_ERROR"
        )


class AIProviderTimeout(ExternalServiceError):
    """AI provider timeout."""

    def __init__(self, provider: str):
        super().__init__(
            message=f"AI provider {provider} timed out",
            service=provider,
            code="AI_PROVIDER_TIMEOUT",
            details={"hint": "Try again or use a different model"}
        )


class AIProviderUnavailable(ExternalServiceError):
    """AI provider unavailable."""

    def __init__(self, provider: str):
        super().__init__(
            message=f"AI provider {provider} is temporarily unavailable",
            service=provider,
            code="AI_PROVIDER_UNAVAILABLE",
            status_code=503,
            details={"hint": "Service will resume shortly"}
        )


# Database Errors
class DatabaseError(MoneyAPIException):
    """Base database error."""

    def __init__(self, message: str = "Database error", details: Optional[Dict] = None):
        super().__init__(
            message=message,
            code="DATABASE_ERROR",
            status_code=500,
            details=details
        )


class DatabaseConnectionError(DatabaseError):
    """Database connection error."""

    def __init__(self, message: str = "Failed to connect to database"):
        super().__init__(
            message=message,
            code="DATABASE_CONNECTION_ERROR"
        )


# Configuration Errors
class ConfigurationError(MoneyAPIException):
    """Configuration error."""

    def __init__(self, message: str = "Configuration error", details: Optional[Dict] = None):
        super().__init__(
            message=message,
            code="CONFIGURATION_ERROR",
            status_code=500,
            details=details
        )
