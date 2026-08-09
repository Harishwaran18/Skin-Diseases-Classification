"""Small shared helpers."""
from __future__ import annotations

import secrets
import string


def random_filename(ext: str, length: int = 24) -> str:
    """Generate a non-enumerable random filename for private storage."""
    alphabet = string.ascii_lowercase + string.digits
    token = "".join(secrets.choice(alphabet) for _ in range(length))
    return f"{token}.{ext.lstrip('.').lower()}"
