"""Validation utilities."""

import re

EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


def validate_email(email: str) -> None:
    """Validate email format."""
    if not EMAIL_PATTERN.match(email):
        raise ValueError(f"Invalid email: {email}")
