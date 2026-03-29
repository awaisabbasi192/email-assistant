"""User authentication module with bcrypt hashing."""

import bcrypt
import logging
from typing import Optional, Dict
from functools import wraps
from flask import session, redirect, url_for, request

logger = logging.getLogger(__name__)


class UserAuthManager:
    """Manages user registration, login, and session handling."""

    def __init__(self, db_manager):
        """
        Initialize authentication manager.

        Args:
            db_manager: DatabaseManager instance
        """
        self.db = db_manager

    def register_user(self, username: str, email: str, password: str) -> Optional[int]:
        """
        Register new user with bcrypt-hashed password.

        Args:
            username: Username (alphanumeric, 3-20 chars)
            email: User email (must be valid)
            password: Password (min 8 chars)

        Returns:
            User ID if successful, None otherwise
        """
        # Validate inputs
        if not self._validate_username(username):
            logger.warning(f"Invalid username format: {username}")
            return None

        if not self._validate_email(email):
            logger.warning(f"Invalid email format: {email}")
            return None

        if not self._validate_password(password):
            logger.warning(f"Password does not meet requirements")
            return None

        # Hash password with bcrypt
        try:
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')
        except Exception as e:
            logger.error(f"Error hashing password: {e}")
            return None

        # Add to database
        try:
            user_id = self.db.add_user(username, email, password_hash)
            if user_id:
                logger.info(f"User registered: {username}")
            return user_id
        except Exception as e:
            logger.error(f"Error registering user: {e}")
            return None

    def authenticate(self, username: str, password: str) -> Optional[Dict]:
        """
        Authenticate user credentials.

        Args:
            username: Username
            password: Password

        Returns:
            User dict if successful, None otherwise
        """
        try:
            user = self.db.get_user_by_username(username)

            if not user:
                logger.warning(f"Login attempt for non-existent user: {username}")
                return None

            # Verify bcrypt hash
            password_bytes = password.encode('utf-8')
            password_hash = user['password_hash'].encode('utf-8')

            if not bcrypt.checkpw(password_bytes, password_hash):
                logger.warning(f"Failed login attempt for user: {username}")
                return None

            # Update last login
            self.db.update_user_last_login(user['id'])

            logger.info(f"User logged in: {username}")
            return user

        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            return None

    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """
        Change user password.

        Args:
            user_id: User ID
            old_password: Current password
            new_password: New password

        Returns:
            True if successful
        """
        try:
            user = self.db.get_user_by_id(user_id)

            if not user:
                logger.warning(f"Password change for non-existent user: {user_id}")
                return False

            # Verify old password
            old_password_bytes = old_password.encode('utf-8')
            password_hash = user['password_hash'].encode('utf-8')

            if not bcrypt.checkpw(old_password_bytes, password_hash):
                logger.warning(f"Failed password change attempt for user: {user_id}")
                return False

            # Validate new password
            if not self._validate_password(new_password):
                logger.warning(f"New password does not meet requirements for user: {user_id}")
                return False

            # Hash new password
            new_password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')

            # Update in database
            # Note: You'll need to add update_user_password method to DatabaseManager
            logger.info(f"Password changed for user: {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error changing password: {e}")
            return False

    def login_required(self, f):
        """Decorator for routes requiring authentication."""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session or not session.get('authenticated'):
                return redirect(url_for('login', next=request.url))
            return f(*args, **kwargs)
        return decorated_function

    def admin_required(self, f):
        """Decorator for routes requiring admin access."""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session or not session.get('authenticated'):
                return redirect(url_for('login', next=request.url))

            # Check if user is admin (user_id = 1)
            if session.get('user_id') != 1:
                return redirect(url_for('dashboard'))

            return f(*args, **kwargs)
        return decorated_function

    # Validation methods

    @staticmethod
    def _validate_username(username: str) -> bool:
        """
        Validate username format.

        Requirements:
        - 3-20 characters
        - Alphanumeric only
        """
        if not username or not isinstance(username, str):
            return False

        username = username.strip()

        if len(username) < 3 or len(username) > 20:
            return False

        if not username.isalnum():
            return False

        return True

    @staticmethod
    def _validate_email(email: str) -> bool:
        """
        Validate email format.

        Simple validation - accepts most email formats.
        """
        if not email or not isinstance(email, str):
            return False

        email = email.strip()

        # Simple email validation
        if '@' not in email or '.' not in email:
            return False

        if len(email) < 5 or len(email) > 254:
            return False

        # Check for valid characters
        invalid_chars = ' ,<>:;'
        if any(char in email for char in invalid_chars):
            return False

        return True

    @staticmethod
    def _validate_password(password: str) -> bool:
        """
        Validate password strength.

        Requirements:
        - Minimum 8 characters
        - At least one uppercase letter OR one digit
        """
        if not password or not isinstance(password, str):
            return False

        if len(password) < 8:
            return False

        # Must have at least one uppercase letter or digit
        has_upper = any(c.isupper() for c in password)
        has_digit = any(c.isdigit() for c in password)

        if not (has_upper or has_digit):
            return False

        return True
