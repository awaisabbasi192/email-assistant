"""Email scheduling and snoozing system."""

import logging
import threading
import time
from datetime import datetime
from typing import List, Dict, Optional
from database import DatabaseManager

logger = logging.getLogger(__name__)


class EmailScheduler:
    """Manages scheduled email sending and snoozed emails."""

    def __init__(self, db: DatabaseManager, check_interval: int = 60):
        """
        Initialize email scheduler.

        Args:
            db: DatabaseManager instance
            check_interval: Seconds between checking for scheduled/snoozed emails
        """
        self.db = db
        self.logger = logging.getLogger(__name__)
        self.check_interval = check_interval
        self.running = False
        self.check_thread: Optional[threading.Thread] = None

    def start(self):
        """Start scheduler background thread."""
        if self.running:
            self.logger.warning("Scheduler already running")
            return

        self.running = True
        self.check_thread = threading.Thread(target=self._check_loop, daemon=True)
        self.check_thread.start()
        self.logger.info(f"Email scheduler started (check interval: {self.check_interval}s)")

    def stop(self):
        """Stop scheduler background thread."""
        self.running = False
        if self.check_thread:
            self.check_thread.join(timeout=5)
        self.logger.info("Email scheduler stopped")

    def _check_loop(self):
        """Background loop to check for scheduled emails."""
        while self.running:
            try:
                self._process_scheduled_emails()
                self._process_snoozed_emails()
                time.sleep(self.check_interval)
            except Exception as e:
                self.logger.error(f"Error in scheduler loop: {e}")
                time.sleep(self.check_interval)

    def _process_scheduled_emails(self):
        """Process emails scheduled for sending."""
        now = datetime.now().isoformat()

        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()

            # Create table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scheduled_emails (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    draft_id INTEGER NOT NULL,
                    scheduled_time TIMESTAMP NOT NULL,
                    status TEXT DEFAULT 'pending',
                    sent_at TIMESTAMP,
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (draft_id) REFERENCES drafts(id) ON DELETE CASCADE
                )
            """)

            # Get emails due for sending
            cursor.execute("""
                SELECT * FROM scheduled_emails
                WHERE status = 'pending' AND scheduled_time <= ?
                ORDER BY scheduled_time ASC
                LIMIT 10
            """, (now,))

            scheduled_emails = [dict(row) for row in cursor.fetchall()]

            for scheduled in scheduled_emails:
                self._send_scheduled_email(scheduled)

        finally:
            conn.close()

    def _send_scheduled_email(self, scheduled: Dict):
        """Send a scheduled email."""
        try:
            draft_id = scheduled['draft_id']

            # Get draft
            draft = self.db.get_draft(draft_id)
            if not draft:
                self.logger.error(f"Draft {draft_id} not found for scheduled email")
                self._mark_scheduled_failed(scheduled['id'], "Draft not found")
                return

            # Get email
            email = self.db.get_email(draft['email_id'])
            if not email:
                self.logger.error(f"Email not found for draft {draft_id}")
                self._mark_scheduled_failed(scheduled['id'], "Email not found")
                return

            # TODO: Integrate with Gmail API to send email
            # For now, just log and mark as sent
            self.logger.info(f"Sending scheduled email (draft {draft_id}) to {email.get('sender', 'unknown')}")
            self._mark_scheduled_sent(scheduled['id'])

        except Exception as e:
            self.logger.error(f"Error sending scheduled email: {e}")
            self._mark_scheduled_failed(scheduled['id'], str(e))

    def _mark_scheduled_sent(self, scheduled_id: int):
        """Mark scheduled email as sent."""
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE scheduled_emails
                SET status = 'sent', sent_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (scheduled_id,))
            conn.commit()
        finally:
            conn.close()

    def _mark_scheduled_failed(self, scheduled_id: int, error_message: str):
        """Mark scheduled email as failed."""
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE scheduled_emails
                SET status = 'failed', error_message = ?
                WHERE id = ?
            """, (error_message, scheduled_id))
            conn.commit()
        finally:
            conn.close()

    def _process_snoozed_emails(self):
        """Re-surface snoozed emails that are due."""
        now = datetime.now().isoformat()

        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()

            # Create table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS snoozed_emails (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    email_id INTEGER NOT NULL,
                    snooze_until TIMESTAMP NOT NULL,
                    snoozed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (email_id) REFERENCES emails(id) ON DELETE CASCADE
                )
            """)

            # Get snoozed emails due to resurface
            cursor.execute("""
                SELECT * FROM snoozed_emails
                WHERE snooze_until <= ?
            """, (now,))

            snoozed = [dict(row) for row in cursor.fetchall()]

            for snooze in snoozed:
                self._resurface_email(snooze)

        finally:
            conn.close()

    def _resurface_email(self, snooze: Dict):
        """Resurface a snoozed email."""
        email_id = snooze['email_id']
        user_id = snooze['user_id']

        self.logger.info(f"Resurfacing snoozed email {email_id} for user {user_id}")

        # Delete snooze record
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM snoozed_emails WHERE id = ?", (snooze['id'],))
            conn.commit()
        finally:
            conn.close()

    def schedule_email(self, user_id: int, draft_id: int, scheduled_time: datetime) -> int:
        """
        Schedule an email for future sending.

        Args:
            user_id: User ID
            draft_id: Draft ID
            scheduled_time: When to send (datetime object)

        Returns:
            Scheduled email ID
        """
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()

            # Create table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scheduled_emails (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    draft_id INTEGER NOT NULL,
                    scheduled_time TIMESTAMP NOT NULL,
                    status TEXT DEFAULT 'pending',
                    sent_at TIMESTAMP,
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (draft_id) REFERENCES drafts(id) ON DELETE CASCADE
                )
            """)

            cursor.execute("""
                INSERT INTO scheduled_emails (user_id, draft_id, scheduled_time)
                VALUES (?, ?, ?)
            """, (user_id, draft_id, scheduled_time.isoformat()))

            conn.commit()
            scheduled_id = cursor.lastrowid
            self.logger.info(f"Scheduled draft {draft_id} for {scheduled_time}")
            return scheduled_id

        finally:
            conn.close()

    def snooze_email(self, user_id: int, email_id: int, snooze_until: datetime) -> int:
        """
        Snooze an email until specified time.

        Args:
            user_id: User ID
            email_id: Email ID
            snooze_until: When to resurface (datetime object)

        Returns:
            Snooze ID
        """
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()

            # Create table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS snoozed_emails (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    email_id INTEGER NOT NULL,
                    snooze_until TIMESTAMP NOT NULL,
                    snoozed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (email_id) REFERENCES emails(id) ON DELETE CASCADE
                )
            """)

            cursor.execute("""
                INSERT INTO snoozed_emails (user_id, email_id, snooze_until)
                VALUES (?, ?, ?)
            """, (user_id, email_id, snooze_until.isoformat()))

            conn.commit()
            snooze_id = cursor.lastrowid
            self.logger.info(f"Snoozed email {email_id} until {snooze_until}")
            return snooze_id

        finally:
            conn.close()

    def cancel_scheduled_email(self, scheduled_id: int) -> bool:
        """
        Cancel a scheduled email.

        Args:
            scheduled_id: Scheduled email ID

        Returns:
            True if cancelled, False otherwise
        """
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE scheduled_emails
                SET status = 'cancelled'
                WHERE id = ? AND status = 'pending'
            """, (scheduled_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def unsnooze_email(self, snooze_id: int) -> bool:
        """
        Unsnooze an email (remove from snooze).

        Args:
            snooze_id: Snooze ID

        Returns:
            True if unsnoozed, False otherwise
        """
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM snoozed_emails WHERE id = ?
            """, (snooze_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def get_scheduled_emails(self, user_id: int) -> List[Dict]:
        """
        Get all scheduled emails for user.

        Args:
            user_id: User ID

        Returns:
            List of scheduled emails
        """
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()

            # Create table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scheduled_emails (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    draft_id INTEGER NOT NULL,
                    scheduled_time TIMESTAMP NOT NULL,
                    status TEXT DEFAULT 'pending',
                    sent_at TIMESTAMP,
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (draft_id) REFERENCES drafts(id) ON DELETE CASCADE
                )
            """)

            cursor.execute("""
                SELECT * FROM scheduled_emails
                WHERE user_id = ? AND status = 'pending'
                ORDER BY scheduled_time ASC
            """, (user_id,))

            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def get_snoozed_emails(self, user_id: int) -> List[Dict]:
        """
        Get all snoozed emails for user.

        Args:
            user_id: User ID

        Returns:
            List of snoozed emails
        """
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()

            # Create table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS snoozed_emails (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    email_id INTEGER NOT NULL,
                    snooze_until TIMESTAMP NOT NULL,
                    snoozed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (email_id) REFERENCES emails(id) ON DELETE CASCADE
                )
            """)

            cursor.execute("""
                SELECT * FROM snoozed_emails
                WHERE user_id = ?
                ORDER BY snooze_until ASC
            """, (user_id,))

            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
