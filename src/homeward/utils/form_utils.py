"""Utilities for form data processing"""

from typing import Any, Optional


def sanitize_form_value(value: Any) -> Optional[Any]:
    """
    Convert empty strings to None for better database storage.

    Args:
        value: The form value to sanitize

    Returns:
        None if value is empty string, otherwise the original value
    """
    if isinstance(value, str) and value.strip() == "":
        return None
    return value


def sanitize_form_data(form_data: dict) -> dict:
    """
    Sanitize all form data values, converting empty strings to None.

    Args:
        form_data: Dictionary of form field values

    Returns:
        Dictionary with empty strings converted to None
    """
    sanitized_data = {}
    for key, value in form_data.items():
        sanitized_data[key] = sanitize_form_value(value)
    return sanitized_data


def get_sanitized_form_value(form_data: dict, key: str, default: Any = None) -> Optional[Any]:
    """
    Get a sanitized form value, converting empty strings to None.

    Args:
        form_data: Dictionary of form field values
        key: The key to retrieve
        default: Default value if key doesn't exist

    Returns:
        Sanitized form value or default
    """
    value = form_data.get(key, default)
    return sanitize_form_value(value)