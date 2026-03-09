"""GROQ API key validation."""

import re


def validate_groq_api_key(api_key: str) -> tuple[bool, str]:
    """
    Validate the format and structure of a GROQ API key.

    Args:
        api_key: The API key string to validate.

    Returns:
        A (is_valid, message) tuple.
    """
    if not api_key or not isinstance(api_key, str):
        return False, "API key is required"

    api_key = api_key.strip()

    if api_key in {"no-key-needed", "123", "test", "demo"}:
        return False, "Please enter a valid GROQ API key"

    if not api_key.startswith("gsk_"):
        return False, "Invalid GROQ API key format. Keys should start with 'gsk_'"

    if len(api_key) < 30:
        return False, "API key too short. Please check your GROQ API key"

    if len(api_key) > 100:
        return False, "API key too long. Please check your GROQ API key"

    if not re.match(r"^gsk_[A-Za-z0-9_]+$", api_key):
        return False, "Invalid characters in API key. Only letters, numbers, and underscores allowed"

    return True, "API key format is valid"
