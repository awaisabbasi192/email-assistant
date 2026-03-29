"""Input validation utilities to prevent injection attacks and data corruption."""

import re
import logging
from typing import Optional, List

logger = logging.getLogger(__name__)


class InputValidator:
    """Validate user inputs to prevent injection attacks and ensure data integrity."""

    # Regex patterns for validation
    EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )

    # Valid priority levels
    VALID_PRIORITIES = {'low', 'normal', 'high', 'urgent'}

    # Valid draft statuses
    VALID_STATUSES = {'pending', 'approved', 'sent', 'deleted'}

    # Valid email categories
    VALID_CATEGORIES = {
        'personal', 'work', 'support', 'marketing', 'bills',
        'social', 'newsletter', 'urgent', 'spam'
    }

    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate email address format.

        Args:
            email: Email address to validate

        Returns:
            True if valid email format, False otherwise
        """
        if not email or not isinstance(email, str):
            return False

        email = email.strip()

        # Check length (RFC 5321 limit is 254)
        if len(email) > 254 or len(email) < 5:
            return False

        # Check format
        if not InputValidator.EMAIL_PATTERN.match(email):
            return False

        return True

    @staticmethod
    def sanitize_string(text: str, max_length: int = 10000) -> str:
        """
        Sanitize string input by removing dangerous characters.

        Args:
            text: String to sanitize
            max_length: Maximum allowed length

        Returns:
            Sanitized string
        """
        if not text or not isinstance(text, str):
            return ""

        # Remove null bytes and dangerous characters
        sanitized = text.replace('\x00', '').replace('<', '').replace('>', '').replace('&', '')
        # Remove most control characters except newlines and tabs
        sanitized = ''.join(c for c in sanitized if ord(c) >= 32 or c in '\n\t')

        # Limit length
        if len(sanitized) > max_length:
            logger.warning(f"String truncated from {len(sanitized)} to {max_length} chars")
            sanitized = sanitized[:max_length]

        return sanitized.strip()

    @staticmethod
    def validate_priority(priority: str) -> bool:
        """
        Validate email priority value.

        Args:
            priority: Priority string to validate

        Returns:
            True if valid priority, False otherwise
        """
        if not priority or not isinstance(priority, str):
            return False

        return priority in InputValidator.VALID_PRIORITIES

    @staticmethod
    def validate_status(status: str) -> bool:
        """
        Validate draft status value.

        Args:
            status: Status string to validate

        Returns:
            True if valid status, False otherwise
        """
        if not status or not isinstance(status, str):
            return False

        return status.lower() in InputValidator.VALID_STATUSES

    @staticmethod
    def validate_category(category: str) -> bool:
        """
        Validate email category.

        Args:
            category: Category string to validate

        Returns:
            True if valid category, False otherwise
        """
        if not category or not isinstance(category, str):
            return False

        return category.lower() in InputValidator.VALID_CATEGORIES

    @staticmethod
    def validate_integer(value: any, min_val: int = 0, max_val: int = 2147483647) -> bool:
        """
        Validate integer within range.

        Args:
            value: Value to validate
            min_val: Minimum allowed value
            max_val: Maximum allowed value

        Returns:
            True if valid integer in range, False otherwise
        """
        try:
            int_val = int(value)
            return min_val <= int_val <= max_val
        except (ValueError, TypeError):
            return False

    @staticmethod
    def validate_date_format(date_str: str) -> bool:
        """
        Validate ISO date format (YYYY-MM-DD).

        Args:
            date_str: Date string to validate

        Returns:
            True if valid ISO date format, False otherwise
        """
        if not date_str or not isinstance(date_str, str):
            return False

        date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
        if not date_pattern.match(date_str):
            return False

        # Validate it's actually a valid date
        try:
            from datetime import datetime
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    @staticmethod
    def validate_sender_email(sender: str) -> bool:
        """
        Validate sender email (often in "Name <email@domain>" format).

        Args:
            sender: Sender string (may include display name)

        Returns:
            True if contains valid email, False otherwise
        """
        if not sender or not isinstance(sender, str):
            return False

        # Extract email from potential "Name <email>" format
        email_match = re.search(r'<([^>]+)>', sender)
        if email_match:
            email = email_match.group(1)
            return InputValidator.validate_email(email)

        # Or it might be just the email
        return InputValidator.validate_email(sender)
