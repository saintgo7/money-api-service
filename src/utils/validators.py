"""Validation utilities."""
import re
from typing import Optional


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password_strength(password: str) -> tuple[bool, Optional[str]]:
    """Validate password strength.

    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"

    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"

    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"

    return True, None


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent directory traversal."""
    # Remove path separators and dangerous characters
    filename = re.sub(r'[/\\]', '', filename)
    filename = re.sub(r'\.\.', '', filename)
    return filename


def validate_api_key_format(key: str) -> bool:
    """Validate API key format."""
    if not key.startswith("sk_"):
        return False

    if len(key) < 20:
        return False

    # Check for valid characters (base64url)
    pattern = r'^sk_[A-Za-z0-9_-]+$'
    return bool(re.match(pattern, key))
