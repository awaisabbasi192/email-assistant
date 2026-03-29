"""Error handling, retry logic, and circuit breaker for resilient operations."""

import logging
import time
from functools import wraps
from typing import Callable, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RetryConfig:
    """Configuration for retry behavior."""

    def __init__(self, max_attempts: int = 3, initial_delay: float = 1.0,
                 max_delay: float = 60.0, exponential_base: float = 2.0):
        """
        Initialize retry configuration.

        Args:
            max_attempts: Maximum number of retry attempts
            initial_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
            exponential_base: Base for exponential backoff
        """
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt number."""
        delay = self.initial_delay * (self.exponential_base ** (attempt - 1))
        return min(delay, self.max_delay)


def retry(config: Optional[RetryConfig] = None, exceptions: tuple = (Exception,)):
    """
    Decorator for retrying function calls with exponential backoff.

    Args:
        config: RetryConfig object (default: 3 attempts, exponential backoff)
        exceptions: Tuple of exceptions to catch and retry on

    Example:
        @retry(exceptions=(requests.RequestException,))
        def call_api():
            return requests.get('http://api.example.com')
    """
    if config is None:
        config = RetryConfig()

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None

            for attempt in range(1, config.max_attempts + 1):
                try:
                    logger.debug(f"Attempt {attempt}/{config.max_attempts}: {func.__name__}")
                    return func(*args, **kwargs)

                except exceptions as e:
                    last_exception = e
                    logger.warning(
                        f"Attempt {attempt}/{config.max_attempts} failed for {func.__name__}: {str(e)}"
                    )

                    if attempt < config.max_attempts:
                        delay = config.get_delay(attempt)
                        logger.info(f"Retrying in {delay:.2f} seconds...")
                        time.sleep(delay)
                    else:
                        logger.error(f"All {config.max_attempts} attempts failed for {func.__name__}")

            raise last_exception

        return wrapper
    return decorator


class CircuitBreaker:
    """Circuit breaker pattern for handling service failures."""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 60.0,
                 name: str = "CircuitBreaker"):
        """
        Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before attempting recovery
            name: Name of the circuit breaker (for logging)
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.name = name
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.is_open = False
        self.is_half_open = False

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection.

        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            Exception: If circuit is open or function fails
        """
        if self.is_open:
            if self._should_attempt_recovery():
                logger.info(f"{self.name}: Attempting recovery (half-open)")
                self.is_half_open = True
            else:
                raise Exception(f"{self.name}: Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result

        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self) -> None:
        """Handle successful call."""
        if self.is_half_open:
            logger.info(f"{self.name}: Recovery successful, circuit CLOSED")
            self.is_open = False
            self.is_half_open = False
            self.failure_count = 0

    def _on_failure(self) -> None:
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            logger.error(
                f"{self.name}: Failure threshold ({self.failure_threshold}) reached. Circuit OPEN"
            )
            self.is_open = True
            self.is_half_open = False

    def _should_attempt_recovery(self) -> bool:
        """Check if circuit should attempt recovery."""
        if not self.last_failure_time:
            return True

        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        return elapsed >= self.recovery_timeout

    def reset(self) -> None:
        """Manually reset circuit breaker."""
        logger.info(f"{self.name}: Circuit breaker reset")
        self.is_open = False
        self.is_half_open = False
        self.failure_count = 0
        self.last_failure_time = None

    def get_status(self) -> str:
        """Get current status of circuit breaker."""
        if self.is_open:
            return "OPEN"
        elif self.is_half_open:
            return "HALF-OPEN"
        else:
            return "CLOSED"


class ServiceHealthChecker:
    """Checks health of external services."""

    def __init__(self):
        """Initialize health checker."""
        self.service_health: dict = {}

    def check_gmail_api(self, gmail_service) -> bool:
        """
        Check if Gmail API is accessible.

        Args:
            gmail_service: Gmail API service object

        Returns:
            True if API is accessible, False otherwise
        """
        try:
            gmail_service.users().getProfile(userId='me').execute()
            self.service_health['gmail'] = 'healthy'
            logger.debug("Gmail API health check: OK")
            return True
        except Exception as e:
            self.service_health['gmail'] = f'unhealthy: {str(e)}'
            logger.warning(f"Gmail API health check failed: {e}")
            return False

    def check_ollama(self, base_url: str = "http://127.0.0.1:11434") -> bool:
        """
        Check if Ollama service is running.

        Args:
            base_url: Ollama base URL

        Returns:
            True if Ollama is accessible, False otherwise
        """
        try:
            import requests
            response = requests.get(f"{base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                self.service_health['ollama'] = 'healthy'
                logger.debug("Ollama health check: OK")
                return True
            else:
                self.service_health['ollama'] = f'unhealthy: {response.status_code}'
                logger.warning(f"Ollama health check failed: Status {response.status_code}")
                return False
        except Exception as e:
            self.service_health['ollama'] = f'unhealthy: {str(e)}'
            logger.warning(f"Ollama health check failed: {e}")
            return False

    def check_database(self, db_file: str = "email_assistant.db") -> bool:
        """
        Check if database is accessible.

        Args:
            db_file: Database file path

        Returns:
            True if database is accessible, False otherwise
        """
        try:
            import sqlite3
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            conn.close()
            self.service_health['database'] = 'healthy'
            logger.debug("Database health check: OK")
            return True
        except Exception as e:
            self.service_health['database'] = f'unhealthy: {str(e)}'
            logger.warning(f"Database health check failed: {e}")
            return False

    def get_health_report(self) -> dict:
        """Get health status of all services."""
        return self.service_health.copy()

    def are_all_healthy(self) -> bool:
        """Check if all services are healthy."""
        return all(
            status == 'healthy'
            for status in self.service_health.values()
        )


class ErrorNotificationManager:
    """Manages error notifications and alerts."""

    def __init__(self, log_file: str = "email_assistant.log"):
        """
        Initialize error notification manager.

        Args:
            log_file: Path to log file
        """
        self.log_file = log_file
        self.error_history: list = []
        self.critical_errors: list = []

    def log_error(self, error_type: str, message: str, severity: str = "warning") -> None:
        """
        Log an error.

        Args:
            error_type: Type of error (e.g., 'api_error', 'database_error')
            message: Error message
            severity: Severity level ('info', 'warning', 'error', 'critical')
        """
        error_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': error_type,
            'message': message,
            'severity': severity
        }
        self.error_history.append(error_entry)

        if severity == 'critical':
            self.critical_errors.append(error_entry)

        if severity == 'critical':
            logger.critical(f"{error_type}: {message}")
        elif severity == 'error':
            logger.error(f"{error_type}: {message}")
        elif severity == 'warning':
            logger.warning(f"{error_type}: {message}")
        else:
            logger.info(f"{error_type}: {message}")

    def get_error_history(self, limit: int = 100) -> list:
        """Get recent error history."""
        return self.error_history[-limit:]

    def get_critical_errors(self) -> list:
        """Get all critical errors."""
        return self.critical_errors.copy()

    def clear_history(self) -> None:
        """Clear error history."""
        self.error_history.clear()
        self.critical_errors.clear()

    def get_error_report(self) -> dict:
        """Get comprehensive error report."""
        return {
            'total_errors': len(self.error_history),
            'critical_errors': len(self.critical_errors),
            'recent_errors': self.get_error_history(10),
            'critical_list': self.critical_errors
        }


class GracefulDegradation:
    """Handles graceful degradation when services fail."""

    @staticmethod
    def get_fallback_reply() -> str:
        """Get fallback reply when reply generation fails."""
        return """Thank you for your email. I've received your message and will review it. I'll get back to you soon.

Best regards"""

    @staticmethod
    def get_fallback_category() -> str:
        """Get fallback category when classification fails."""
        return "uncategorized"

    @staticmethod
    def handle_ollama_failure(original_email: dict) -> str:
        """
        Handle Ollama failure with template-based reply.

        Args:
            original_email: Original email data

        Returns:
            Template-based reply
        """
        sender_name = original_email.get('sender', 'there').split('<')[0].strip()
        subject = original_email.get('subject', '')

        if 'question' in subject.lower() or 'help' in subject.lower():
            return f"""Hi {sender_name},

Thank you for reaching out. I appreciate your question and will review it carefully. I'll provide a detailed response shortly.

Best regards"""

        elif 'feedback' in subject.lower() or 'suggestion' in subject.lower():
            return f"""Hi {sender_name},

Thank you for sharing your feedback. Your input is valuable to us, and we appreciate you taking the time to reach out.

Best regards"""

        else:
            return GracefulDegradation.get_fallback_reply()
