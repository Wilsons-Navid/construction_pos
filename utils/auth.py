"""Simple authentication utilities."""

import hashlib

_current_user = None


def hash_password(password: str) -> str:
    """Return a SHA-256 hash for the given password."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against an existing hash."""
    return hash_password(password) == password_hash


def set_current_user(user):
    """Store the currently authenticated user."""
    global _current_user
    _current_user = user


def get_current_user():
    """Get the currently authenticated user, if any."""
    return _current_user

