"""Email threading and conversation management."""

import logging
import json
import re
from typing import List, Dict, Optional
from database import DatabaseManager

logger = logging.getLogger(__name__)


class ThreadManager:
    """Manages email conversation threading and context extraction."""

    def __init__(self, db: DatabaseManager):
        """
        Initialize thread manager.

        Args:
            db: DatabaseManager instance
        """
        self.db = db
        self.logger = logging.getLogger(__name__)

    def group_emails_by_thread(self, emails: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Group emails by conversation thread.

        Uses Gmail thread ID if available, otherwise falls back to
        References and In-Reply-To headers for grouping.

        Args:
            emails: List of email dictionaries

        Returns:
            Dictionary mapping thread_id to list of emails in that thread
        """
        threads = {}

        for email in emails:
            thread_key = self._get_thread_key(email)

            if thread_key not in threads:
                threads[thread_key] = []

            threads[thread_key].append(email)

        # Sort emails within each thread by date
        for thread_key in threads:
            threads[thread_key].sort(
                key=lambda e: e.get('received_at', e.get('created_at', '')),
                reverse=False  # Oldest first
            )

        self.logger.info(f"Grouped {len(emails)} emails into {len(threads)} threads")
        return threads

    def _get_thread_key(self, email: Dict) -> str:
        """
        Determine unique thread key for email.

        Uses Gmail thread ID if available, otherwise uses References
        headers or subject-based grouping.

        Args:
            email: Email dictionary

        Returns:
            Thread key string
        """
        # Use Gmail thread ID if available
        if 'thread_id' in email and email['thread_id']:
            return email['thread_id']

        # Use References header if available
        if 'references' in email and email['references']:
            # References is a space-separated list of Message-IDs
            refs = email['references'].split()
            if refs:
                return refs[0]  # Use root message as thread key

        # Use In-Reply-To header if available
        if 'in_reply_to' in email and email['in_reply_to']:
            return email['in_reply_to']

        # Fall back to subject-based threading
        subject = self._normalize_subject(email.get('subject', ''))

        # Use subject + first sender as thread key
        sender = email.get('sender', '').split('<')[-1].rstrip('>')

        return f"{subject}::{sender}"

    def _normalize_subject(self, subject: str) -> str:
        """
        Normalize subject for threading (remove Re:, Fwd:, etc.).

        Args:
            subject: Email subject line

        Returns:
            Normalized subject
        """
        if not subject:
            return ""

        # Remove common prefixes
        prefixes = [
            r'^re:\s*',
            r'^fwd:\s*',
            r'^fw:\s*',
            r'^\[.*?\]\s*',
            r'^re\[.*?\]:\s*',
        ]

        normalized = subject.lower().strip()

        for prefix in prefixes:
            normalized = re.sub(prefix, '', normalized, flags=re.IGNORECASE)

        return normalized.strip()

    def get_thread_context(self, user_id: int, email_id: int, max_history: int = 10) -> List[Dict]:
        """
        Get full conversation context for an email (thread history).

        Returns emails in chronological order (oldest first).

        Args:
            user_id: User ID
            email_id: Email ID to get thread for
            max_history: Maximum number of emails to return

        Returns:
            List of emails in thread, in chronological order
        """
        email = self.db.get_email(email_id)

        if not email:
            self.logger.warning(f"Email {email_id} not found")
            return []

        # Get thread key
        thread_key = self._get_thread_key(email)

        if not thread_key:
            self.logger.warning(f"Could not determine thread key for email {email_id}")
            return [email]

        # Query database for all emails in this thread
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()

            # Search by thread_id, references, or in_reply_to
            cursor.execute("""
                SELECT * FROM emails
                WHERE user_id = ? AND (
                    thread_id = ? OR
                    references LIKE ? OR
                    in_reply_to = ? OR
                    (LOWER(subject) LIKE ? AND sender LIKE ?)
                )
                ORDER BY received_at ASC
                LIMIT ?
            """, (
                user_id,
                thread_key,
                f"%{thread_key}%",
                thread_key,
                f"%{self._extract_subject(thread_key)}%",
                self._extract_sender(thread_key),
                max_history
            ))

            thread_emails = [dict(row) for row in cursor.fetchall()]

            if not thread_emails:
                # If no matches found, return just this email
                return [email]

            self.logger.info(f"Retrieved {len(thread_emails)} emails for thread {thread_key}")
            return thread_emails

        finally:
            conn.close()

    def _extract_subject(self, thread_key: str) -> str:
        """Extract subject from thread key."""
        if '::' in thread_key:
            return thread_key.split('::')[0]
        return thread_key

    def _extract_sender(self, thread_key: str) -> str:
        """Extract sender from thread key."""
        if '::' in thread_key:
            return f"%{thread_key.split('::')[1]}%"
        return "%"

    def generate_context_aware_prompt(self, current_email: Dict, thread_history: List[Dict]) -> str:
        """
        Generate LLM prompt with full thread context.

        Includes conversation history for context-aware reply generation.

        Args:
            current_email: Current email to reply to
            thread_history: Full thread history (chronological order)

        Returns:
            Prompt string with thread context
        """
        if len(thread_history) <= 1:
            # No thread history, return simple prompt
            return self._simple_prompt(current_email)

        # Build conversation history context
        context = "CONVERSATION HISTORY:\n"
        context += "=" * 60 + "\n\n"

        for i, email in enumerate(thread_history[:-1], 1):  # Exclude current email
            sender = email.get('sender', 'Unknown').split('<')[0].strip()
            subject = email.get('subject', 'No Subject')
            body = email.get('body', '')[:300]  # Limit length
            received_at = email.get('received_at', email.get('created_at', 'Unknown'))

            context += f"[{i}] From: {sender} ({received_at})\n"
            context += f"    Subject: {subject}\n"
            context += f"    Message: {body}...\n\n"

        # Add current email
        context += "CURRENT EMAIL TO REPLY TO:\n"
        context += "-" * 60 + "\n"
        current_sender = current_email.get('sender', 'Unknown').split('<')[0].strip()
        context += f"From: {current_sender}\n"
        context += f"Subject: {current_email.get('subject', 'No Subject')}\n"
        context += f"Message: {current_email.get('body', '')}\n\n"

        context += "TASK:\n"
        context += "Generate a professional, contextual reply that considers the entire conversation history above.\n"
        context += "Keep the reply concise (2-4 sentences) unless more detail is needed.\n"

        return context

    def _simple_prompt(self, email: Dict) -> str:
        """Generate simple prompt for single email (no thread context)."""
        subject = email.get('subject', 'No Subject')
        sender = email.get('sender', 'Unknown').split('<')[0].strip()
        body = email.get('body', '')

        prompt = f"""Generate a professional email reply to:

From: {sender}
Subject: {subject}

Message:
{body}

Write a concise, professional response (2-4 sentences). Be friendly but formal."""

        return prompt

    def store_thread_info(self, user_id: int, email_id: int, thread_id: str,
                         in_reply_to: Optional[str] = None,
                         references: Optional[str] = None) -> None:
        """
        Store threading information for an email.

        Args:
            user_id: User ID
            email_id: Email ID
            thread_id: Thread ID
            in_reply_to: Message-ID this email is replying to
            references: Message-IDs in thread
        """
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE emails
                SET thread_id = ?, in_reply_to = ?, references = ?
                WHERE id = ? AND user_id = ?
            """, (thread_id, in_reply_to, references, email_id, user_id))

            conn.commit()
            logger.debug(f"Stored threading info for email {email_id}")

        except Exception as e:
            logger.error(f"Error storing thread info: {e}")
            raise
        finally:
            conn.close()

    def get_thread_summary(self, user_id: int, email_id: int) -> Dict:
        """
        Get summary statistics for a thread.

        Args:
            user_id: User ID
            email_id: Email ID in thread

        Returns:
            Dictionary with thread summary
        """
        thread_emails = self.get_thread_context(user_id, email_id)

        if not thread_emails:
            return {
                'total_messages': 0,
                'participants': [],
                'date_range': None,
                'subjects': []
            }

        senders = set(e.get('sender', 'Unknown').split('<')[0].strip() for e in thread_emails)
        subjects = set(self._normalize_subject(e.get('subject', '')) for e in thread_emails)

        dates = [e.get('received_at', e.get('created_at', '')) for e in thread_emails]
        dates = [d for d in dates if d]

        return {
            'total_messages': len(thread_emails),
            'participants': list(senders),
            'date_range': {
                'earliest': min(dates) if dates else None,
                'latest': max(dates) if dates else None
            },
            'subjects': list(subjects)
        }
