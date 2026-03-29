"""Email processing and Gmail operations."""

import base64
import logging
import os
import re
from email.mime.text import MIMEText
from typing import List, Dict, Optional, Tuple
from googleapiclient.errors import HttpError
from database import DatabaseManager

logger = logging.getLogger(__name__)

# Validation patterns
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')


class EmailProcessor:
    """Handles email fetching, parsing, and Gmail operations."""

    def __init__(self, gmail_service, db_manager: Optional[DatabaseManager] = None, user_id: int = 1):
        """
        Initialize email processor.

        Args:
            gmail_service: Authenticated Gmail API service
            db_manager: DatabaseManager instance for storing emails
            user_id: User ID for multi-user support (defaults to 1 for backward compatibility)
        """
        self.service = gmail_service
        self.user_id = user_id
        if db_manager:
            self.db = db_manager
        else:
            # Use database file from parent directory if it exists
            db_path = 'email_assistant.db'
            parent_db = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'email_assistant.db')
            if os.path.exists(parent_db):
                db_path = parent_db
            self.db = DatabaseManager(db_path)

    def get_unread_emails(self, max_results: int = 10, exclude_labels: List[str] = None, skip_keywords: List[str] = None) -> List[Dict]:
        """
        Fetch unread emails from Gmail, filtering out system/auto-reply emails.

        Args:
            max_results: Maximum number of emails to retrieve
            exclude_labels: Labels to exclude from results
            skip_keywords: Keywords to skip (no-reply, alerts, etc)

        Returns:
            List of email dictionaries with subject, sender, and body
        """
        try:
            exclude_labels = exclude_labels or []
            skip_keywords = skip_keywords or []

            # Build query for unread emails
            query = 'is:unread'

            # Exclude certain labels
            for label in exclude_labels:
                query += f' -label:{label}'

            # Get message IDs
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()

            messages = results.get('messages', [])
            logger.info(f"Found {len(messages)} unread emails")

            emails = []
            for message in messages:
                email_data = self._parse_message(message['id'], skip_keywords)
                if email_data:
                    emails.append(email_data)

            return emails

        except HttpError as error:
            logger.error(f"Gmail API error: {error}")
            return []

    def _parse_message(self, message_id: str, skip_keywords: List[str] = None) -> Optional[Dict]:
        """
        Parse a Gmail message, skipping system/auto-reply emails.

        Args:
            message_id: Gmail message ID
            skip_keywords: Keywords to skip (no-reply, alerts, etc)

        Returns:
            Dictionary with email data or None if parsing fails or should be skipped
        """
        try:
            skip_keywords = skip_keywords or []

            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()

            headers = message['payload'].get('headers', [])
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
            to = next((h['value'] for h in headers if h['name'] == 'To'), '')
            message_id_header = next((h['value'] for h in headers if h['name'] == 'Message-ID'), '')

            # Skip no-reply and system emails
            sender_lower = sender.lower()
            subject_lower = subject.lower()

            # Skip marketing/system domains
            system_domains = ['info.', 'contact@info.', 'marketing@', 'noreply@', 'no-reply@',
                            'notification@', 'alert@', 'system@', 'bot@', 'auto@', 'donotreply@',
                            'estatement@', 'ereceipt@', 'billing@', 'invoice@', 'receipt@']

            for domain in system_domains:
                if domain in sender_lower:
                    logger.debug(f"Skipping email from {sender}: system domain")
                    return None

            for keyword in skip_keywords:
                if keyword.lower() in sender_lower or keyword.lower() in subject_lower:
                    logger.debug(f"Skipping email from {sender}: contains '{keyword}'")
                    return None

            # Extract body
            body = self._get_message_body(message['payload'])

            email_data = {
                'message_id': message_id,
                'message_id_header': message_id_header,
                'subject': subject,
                'sender': sender,
                'to': to,
                'body': body[:1000]  # Limit body length for processing
            }

            # Store in database
            try:
                email_id = self.db.add_email(
                    user_id=self.user_id,
                    message_id=message_id,
                    sender=sender,
                    subject=subject,
                    body=body[:1000]
                )
                email_data['email_id'] = email_id
            except Exception as e:
                logger.debug(f"Could not store email in database: {e}")

            return email_data

        except Exception as e:
            logger.error(f"Error parsing message {message_id}: {e}")
            return None

    def _get_message_body(self, payload: Dict) -> str:
        """
        Extract message body from payload.

        Args:
            payload: Message payload

        Returns:
            Message body text
        """
        try:
            if 'parts' in payload:
                # Multipart message
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain':
                        if 'data' in part['body']:
                            return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
            else:
                # Single part message
                if 'body' in payload and 'data' in payload['body']:
                    return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')

            return ''

        except Exception as e:
            logger.warning(f"Error extracting message body: {e}")
            return ''

    def create_draft(self, to: str, subject: str, body: str) -> Optional[str]:
        """
        Create a draft email in Gmail.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body

        Returns:
            Draft message ID or None if creation fails
        """
        try:
            message = MIMEText(body)
            message['To'] = to
            message['Subject'] = subject

            # Add In-Reply-To and References headers for conversation threading
            create_message = {
                'message': {
                    'raw': base64.urlsafe_b64encode(
                        message.as_bytes()
                    ).decode()
                }
            }

            draft = self.service.users().drafts().create(
                userId='me',
                body=create_message
            ).execute()

            draft_id = draft['id']
            logger.info(f"Created draft {draft_id} for recipient {to}")
            return draft_id

        except HttpError as error:
            logger.error(f"Error creating draft: {error}")
            return None

    def create_draft_with_reply_headers(self, original_email: Dict, reply_body: str) -> Optional[str]:
        """
        Create a draft that's a reply to an original email.

        Args:
            original_email: Original email dictionary
            reply_body: Reply message body

        Returns:
            Draft message ID or None if creation fails
        """
        try:
            subject = original_email['subject']
            if not subject.startswith('Re:'):
                subject = f"Re: {subject}"

            message = MIMEText(reply_body)
            message['To'] = original_email['sender']
            message['Subject'] = subject
            message['In-Reply-To'] = original_email['message_id_header']
            message['References'] = original_email['message_id_header']

            create_message = {
                'message': {
                    'raw': base64.urlsafe_b64encode(
                        message.as_bytes()
                    ).decode()
                }
            }

            draft = self.service.users().drafts().create(
                userId='me',
                body=create_message
            ).execute()

            draft_id = draft['id']
            logger.info(f"Created reply draft {draft_id} for {original_email['sender']}")
            return draft_id

        except HttpError as error:
            logger.error(f"Error creating reply draft: {error}")
            return None

    def mark_as_read(self, message_id: str) -> bool:
        """
        Mark an email as read.

        Args:
            message_id: Gmail message ID

        Returns:
            True if successful, False otherwise
        """
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            logger.debug(f"Marked message {message_id} as read")
            return True

        except HttpError as error:
            logger.error(f"Error marking message as read: {error}")
            return False

    def add_label_to_message(self, message_id: str, label_name: str) -> bool:
        """
        Add a label to an email message.

        Args:
            message_id: Gmail message ID
            label_name: Name of label to add

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get or create label
            label_id = self._get_or_create_label(label_name)
            if not label_id:
                return False

            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'addLabelIds': [label_id]}
            ).execute()
            logger.debug(f"Added label '{label_name}' to message {message_id}")
            return True

        except HttpError as error:
            logger.error(f"Error adding label: {error}")
            return False

    def _get_or_create_label(self, label_name: str) -> Optional[str]:
        """
        Get label ID or create label if it doesn't exist.

        Args:
            label_name: Name of label

        Returns:
            Label ID or None if operation fails
        """
        try:
            # Get all labels
            results = self.service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])

            # Check if label exists
            for label in labels:
                if label['name'] == label_name:
                    return label['id']

            # Create label if it doesn't exist
            label_body = {
                'name': label_name,
                'labelListVisibility': 'labelShow',
                'messageListVisibility': 'show'
            }

            created_label = self.service.users().labels().create(
                userId='me',
                body=label_body
            ).execute()

            logger.info(f"Created new label: {label_name}")
            return created_label['id']

        except HttpError as error:
            logger.error(f"Error managing labels: {error}")
            return None

    def validate_email_address(self, email: str) -> bool:
        """
        Validate email address format.

        Args:
            email: Email address to validate

        Returns:
            True if valid, False otherwise
        """
        if not email or not isinstance(email, str):
            return False
        return bool(EMAIL_PATTERN.match(email.strip()))

    def search_emails(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search emails using Gmail query.

        Args:
            query: Gmail search query
            max_results: Maximum results to return

        Returns:
            List of email dictionaries
        """
        try:
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()

            messages = results.get('messages', [])
            emails = []

            for message in messages:
                email_data = self._parse_message(message['id'])
                if email_data:
                    emails.append(email_data)

            logger.info(f"Found {len(emails)} emails matching query: {query}")
            return emails

        except HttpError as error:
            logger.error(f"Gmail API search error: {error}")
            return []

    def get_email_thread(self, message_id: str) -> List[Dict]:
        """
        Get all messages in a thread.

        Args:
            message_id: Gmail message ID

        Returns:
            List of email messages in thread
        """
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()

            thread_id = message.get('threadId')
            if not thread_id:
                return []

            thread = self.service.users().threads().get(
                userId='me',
                id=thread_id
            ).execute()

            messages = thread.get('messages', [])
            thread_emails = []

            for msg in messages:
                email_data = self._parse_message(msg['id'])
                if email_data:
                    thread_emails.append(email_data)

            return thread_emails

        except HttpError as error:
            logger.error(f"Error retrieving thread: {error}")
            return []
