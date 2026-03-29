"""Authentication utilities with password hashing and management."""

import bcrypt
import secrets
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class PasswordManager:
    """Manage password hashing and verification using bcrypt."""

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash password using bcrypt.

        Args:
            password: Plain text password

        Returns:
            Hashed password string
        """
        if not password:
            raise ValueError("Password cannot be empty")

        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """
        Verify password against hash.

        Args:
            password: Plain text password to verify
            password_hash: Hashed password to compare against

        Returns:
            True if password matches hash, False otherwise
        """
        try:
            return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        except (ValueError, TypeError) as e:
            logger.warning(f"Error verifying password: {e}")
            return False

    @staticmethod
    def generate_secure_key(length: int = 32) -> str:
        """
        Generate a cryptographically secure random key.

        Args:
            length: Length of key in bytes

        Returns:
            Hex string of random bytes
        """
        return secrets.token_hex(length)
