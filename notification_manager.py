"""Desktop and in-app notification system with user preferences."""

import logging
import threading
from datetime import datetime, time
from typing import Dict, Optional
from database import DatabaseManager

logger = logging.getLogger(__name__)

# Try to import platform-specific notification libraries
WINDOWS_NOTIFICATIONS = False
try:
    from win10toast import ToastNotifier
    WINDOWS_NOTIFICATIONS = True
except ImportError:
    logger.debug("win10toast not available - Windows notifications disabled")


class NotificationManager:
    """Manages desktop and in-app notifications with preferences."""

    def __init__(self, db: DatabaseManager):
        """
        Initialize notification manager.

        Args:
            db: DatabaseManager instance
        """
        self.db = db
        self.logger = logging.getLogger(__name__)

        # Initialize Windows notifier if available
        self.toaster = ToastNotifier() if WINDOWS_NOTIFICATIONS else None

    def should_notify(self, user_id: int, priority: str) -> bool:
        """
        Check if notification should be sent based on preferences.

        Args:
            user_id: User ID
            priority: Email priority (low, normal, high, urgent)

        Returns:
            True if notification should be sent, False otherwise
        """
        prefs = self.get_notification_preferences(user_id)

        # Check if notifications enabled
        if not prefs.get('desktop_notifications', True):
            self.logger.debug("Notifications disabled for user")
            return False

        # Check quiet hours
        if prefs.get('quiet_hours_enabled', False):
            if self._is_quiet_hours(prefs):
                self.logger.debug("Notifications suppressed - quiet hours active")
                return False

        # Check priority settings
        priority_lower = priority.lower() if priority else 'normal'

        if priority_lower == 'urgent' and prefs.get('notify_urgent', True):
            return True
        elif priority_lower == 'high' and prefs.get('notify_important', True):
            return True
        elif priority_lower == 'normal' and prefs.get('notify_normal', False):
            return True
        elif priority_lower == 'low' and prefs.get('notify_low', False):
            return False

        return prefs.get('notify_normal', False)

    def _is_quiet_hours(self, prefs: Dict) -> bool:
        """
        Check if current time is within quiet hours.

        Args:
            prefs: User notification preferences

        Returns:
            True if in quiet hours, False otherwise
        """
        now = datetime.now().time()
        start_str = prefs.get('quiet_hours_start', '22:00')
        end_str = prefs.get('quiet_hours_end', '08:00')

        try:
            start_time = datetime.strptime(start_str, '%H:%M').time()
            end_time = datetime.strptime(end_str, '%H:%M').time()

            if start_time < end_time:
                # Normal range (e.g., 08:00 - 22:00)
                return not (start_time <= now <= end_time)
            else:
                # Overnight range (e.g., 22:00 - 08:00)
                return start_time <= now or now <= end_time
        except ValueError:
            self.logger.warning("Invalid time format in quiet hours settings")
            return False

    def send_notification(self, title: str, message: str, priority: str = 'normal'):
        """
        Send desktop notification.

        Args:
            title: Notification title
            message: Notification message
            priority: Notification priority (affects icon/style)
        """
        if not self.toaster:
            self.logger.debug(f"Desktop notifications not available. Title: {title}, Message: {message}")
            return

        try:
            # Add priority indicator to title
            priority_lower = (priority or 'normal').lower()
            if priority_lower == 'urgent':
                display_title = f"🔴 {title}"
            elif priority_lower == 'high':
                display_title = f"🟠 {title}"
            else:
                display_title = f"✉️ {title}"

            self.toaster.show_toast(
                title=display_title,
                msg=message,
                duration=10,
                threaded=True
            )

            self.logger.info(f"Notification sent: {title}")

        except Exception as e:
            self.logger.warning(f"Error sending desktop notification: {e}")

    def notify_new_email(self, user_id: int, email: Dict) -> bool:
        """
        Send notification for new email.

        Args:
            user_id: User ID
            email: Email dictionary

        Returns:
            True if notification sent, False otherwise
        """
        priority = email.get('priority', 'normal')

        if not self.should_notify(user_id, priority):
            return False

        sender = email.get('sender', 'Unknown').split('<')[0].strip()
        subject = email.get('subject', 'No Subject')

        title = f"New Email from {sender}"
        message = subject[:80]  # Truncate long subjects

        self.send_notification(title, message, priority)
        return True

    def notify_draft_ready(self, user_id: int, sender: str, subject: str):
        """
        Notify user when draft is ready for review.

        Args:
            user_id: User ID
            sender: Original email sender
            subject: Original email subject
        """
        if not self.should_notify(user_id, 'normal'):
            return

        title = "Draft Ready for Review"
        message = f"Reply to {sender}: {subject[:60]}"

        self.send_notification(title, message, 'normal')

    def get_notification_preferences(self, user_id: int) -> Dict:
        """
        Get notification preferences for user.

        Args:
            user_id: User ID

        Returns:
            Dictionary with preference settings
        """
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()

            # Create table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notification_preferences (
                    user_id INTEGER PRIMARY KEY,
                    desktop_notifications BOOLEAN DEFAULT 1,
                    notify_urgent BOOLEAN DEFAULT 1,
                    notify_important BOOLEAN DEFAULT 1,
                    notify_normal BOOLEAN DEFAULT 0,
                    notify_low BOOLEAN DEFAULT 0,
                    quiet_hours_enabled BOOLEAN DEFAULT 0,
                    quiet_hours_start TEXT DEFAULT '22:00',
                    quiet_hours_end TEXT DEFAULT '08:00',
                    daily_digest_enabled BOOLEAN DEFAULT 0,
                    daily_digest_time TEXT DEFAULT '09:00',
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)

            cursor.execute("""
                SELECT * FROM notification_preferences
                WHERE user_id = ?
            """, (user_id,))

            row = cursor.fetchone()
            if row:
                return dict(row)
            else:
                # Return defaults
                return {
                    'desktop_notifications': True,
                    'notify_urgent': True,
                    'notify_important': True,
                    'notify_normal': False,
                    'notify_low': False,
                    'quiet_hours_enabled': False,
                    'quiet_hours_start': '22:00',
                    'quiet_hours_end': '08:00',
                    'daily_digest_enabled': False,
                    'daily_digest_time': '09:00'
                }
        finally:
            conn.close()

    def update_notification_preferences(self, user_id: int, prefs: Dict) -> bool:
        """
        Update notification preferences for user.

        Args:
            user_id: User ID
            prefs: Dictionary of preference settings

        Returns:
            True if successful, False otherwise
        """
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()

            # Create table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notification_preferences (
                    user_id INTEGER PRIMARY KEY,
                    desktop_notifications BOOLEAN DEFAULT 1,
                    notify_urgent BOOLEAN DEFAULT 1,
                    notify_important BOOLEAN DEFAULT 1,
                    notify_normal BOOLEAN DEFAULT 0,
                    notify_low BOOLEAN DEFAULT 0,
                    quiet_hours_enabled BOOLEAN DEFAULT 0,
                    quiet_hours_start TEXT DEFAULT '22:00',
                    quiet_hours_end TEXT DEFAULT '08:00',
                    daily_digest_enabled BOOLEAN DEFAULT 0,
                    daily_digest_time TEXT DEFAULT '09:00',
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)

            cursor.execute("""
                INSERT OR REPLACE INTO notification_preferences
                (user_id, desktop_notifications, notify_urgent, notify_important,
                 notify_normal, notify_low, quiet_hours_enabled,
                 quiet_hours_start, quiet_hours_end,
                 daily_digest_enabled, daily_digest_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                int(prefs.get('desktop_notifications', True)),
                int(prefs.get('notify_urgent', True)),
                int(prefs.get('notify_important', True)),
                int(prefs.get('notify_normal', False)),
                int(prefs.get('notify_low', False)),
                int(prefs.get('quiet_hours_enabled', False)),
                prefs.get('quiet_hours_start', '22:00'),
                prefs.get('quiet_hours_end', '08:00'),
                int(prefs.get('daily_digest_enabled', False)),
                prefs.get('daily_digest_time', '09:00')
            ))

            conn.commit()
            self.logger.info(f"Updated notification preferences for user {user_id}")
            return True

        except Exception as e:
            self.logger.error(f"Error updating preferences: {e}")
            return False
        finally:
            conn.close()
