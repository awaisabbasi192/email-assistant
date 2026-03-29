"""Email attachment handling and management."""

import logging
import os
import base64
import mimetypes
from pathlib import Path
from typing import List, Dict, Optional
from database import DatabaseManager

logger = logging.getLogger(__name__)


class AttachmentManager:
    """Manages email attachments - detection, download, and preview."""

    def __init__(self, db: DatabaseManager, storage_path: str = "attachments"):
        """
        Initialize attachment manager.

        Args:
            db: DatabaseManager instance
            storage_path: Directory to store downloaded attachments
        """
        self.db = db
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True, parents=True)
        self.logger = logging.getLogger(__name__)

        # File types that can be previewed in browser
        self.previewable_types = {
            'image/png', 'image/jpeg', 'image/gif', 'image/webp',
            'application/pdf',
            'text/plain', 'text/html', 'text/csv'
        }

    def extract_attachments(self, gmail_service, message: Dict) -> List[Dict]:
        """
        Extract attachment metadata from Gmail message.

        Args:
            gmail_service: Gmail API service
            message: Gmail message object

        Returns:
            List of attachment info dictionaries
        """
        attachments = []

        if 'payload' not in message:
            return attachments

        def process_parts(parts, parent_id=None):
            """Recursively process message parts."""
            for part in parts:
                if 'filename' in part and part['filename']:
                    attachment_info = {
                        'filename': part['filename'],
                        'mime_type': part.get('mimeType', 'application/octet-stream'),
                        'size_bytes': part['body'].get('size', 0),
                        'attachment_id': part['body'].get('attachmentId', '')
                    }
                    attachments.append(attachment_info)
                    self.logger.debug(f"Found attachment: {part['filename']}")

                # Recursively process nested parts
                if 'parts' in part:
                    process_parts(part['parts'], part.get('partId'))

        # Process message parts
        if 'parts' in message['payload']:
            process_parts(message['payload']['parts'])

        return attachments

    def store_attachment_metadata(self, user_id: int, email_id: int, attachments: List[Dict]) -> None:
        """
        Store attachment metadata in database.

        Args:
            user_id: User ID
            email_id: Email ID
            attachments: List of attachment dictionaries
        """
        if not attachments:
            return

        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()

            # Create attachments table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS attachments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email_id INTEGER NOT NULL,
                    filename TEXT NOT NULL,
                    mime_type TEXT,
                    size_bytes INTEGER,
                    attachment_id TEXT,
                    file_path TEXT,
                    is_downloaded BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (email_id) REFERENCES emails(id) ON DELETE CASCADE
                )
            """)

            # Insert attachments
            for attachment in attachments:
                cursor.execute("""
                    INSERT INTO attachments
                    (email_id, filename, mime_type, size_bytes, attachment_id)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    email_id,
                    attachment['filename'],
                    attachment['mime_type'],
                    attachment['size_bytes'],
                    attachment['attachment_id']
                ))

            conn.commit()
            self.logger.info(f"Stored {len(attachments)} attachments for email {email_id}")

        finally:
            conn.close()

    def download_attachment(self, gmail_service, message_id: str, attachment_id: str,
                          filename: str) -> Optional[str]:
        """
        Download attachment from Gmail and store locally.

        Args:
            gmail_service: Gmail API service
            message_id: Gmail message ID
            attachment_id: Gmail attachment ID
            filename: Attachment filename

        Returns:
            Local file path if successful, None otherwise
        """
        try:
            # Get attachment data from Gmail
            attachment = gmail_service.users().messages().attachments().get(
                userId='me',
                messageId=message_id,
                id=attachment_id
            ).execute()

            # Decode attachment data
            data = base64.urlsafe_b64decode(attachment['data'])

            # Create safe filename
            safe_filename = self._sanitize_filename(filename)
            file_path = self.storage_path / safe_filename

            # Handle duplicate filenames
            counter = 1
            while file_path.exists():
                name, ext = os.path.splitext(safe_filename)
                file_path = self.storage_path / f"{name}_{counter}{ext}"
                counter += 1

            # Save to disk
            with open(file_path, 'wb') as f:
                f.write(data)

            self.logger.info(f"Downloaded attachment: {file_path}")
            return str(file_path)

        except Exception as e:
            self.logger.error(f"Error downloading attachment: {e}")
            return None

    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename for safe storage.

        Args:
            filename: Original filename

        Returns:
            Safe filename
        """
        # Remove path separators and dangerous characters
        safe_name = filename.replace('/', '_').replace('\\', '_')
        safe_name = ''.join(c for c in safe_name if c.isalnum() or c in '._- ')
        return safe_name[:255]  # Limit to 255 chars

    def get_attachments_for_email(self, email_id: int) -> List[Dict]:
        """
        Get all attachments for an email.

        Args:
            email_id: Email ID

        Returns:
            List of attachment dictionaries
        """
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM attachments
                WHERE email_id = ?
                ORDER BY filename
            """, (email_id,))

            return [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            self.logger.warning(f"Could not retrieve attachments: {e}")
            return []
        finally:
            conn.close()

    def is_previewable(self, mime_type: str) -> bool:
        """
        Check if attachment type can be previewed in browser.

        Args:
            mime_type: MIME type string

        Returns:
            True if previewable, False otherwise
        """
        return mime_type in self.previewable_types

    def get_attachment_context(self, email_id: int) -> str:
        """
        Generate text description of attachments for AI context.

        Used by LLM to understand email has attachments and include
        this information in reply generation.

        Args:
            email_id: Email ID

        Returns:
            Text description of attachments
        """
        attachments = self.get_attachments_for_email(email_id)

        if not attachments:
            return ""

        context = f"\n\nATTACHMENTS ({len(attachments)}):\n"
        for attachment in attachments:
            filename = attachment['filename']
            size_kb = (attachment['size_bytes'] or 0) / 1024
            mime_type = attachment['mime_type'] or 'unknown'

            context += f"  • {filename} ({size_kb:.1f} KB, {mime_type})\n"

        return context

    def update_download_status(self, attachment_id: int, file_path: str) -> None:
        """
        Update download status for an attachment.

        Args:
            attachment_id: Attachment ID
            file_path: Downloaded file path
        """
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE attachments
                SET is_downloaded = 1, file_path = ?
                WHERE id = ?
            """, (file_path, attachment_id))

            conn.commit()

        finally:
            conn.close()

    def get_attachment_by_id(self, attachment_id: int) -> Optional[Dict]:
        """
        Get attachment details by ID.

        Args:
            attachment_id: Attachment ID

        Returns:
            Attachment dictionary or None
        """
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM attachments WHERE id = ?
            """, (attachment_id,))

            row = cursor.fetchone()
            return dict(row) if row else None

        finally:
            conn.close()

    def get_emails_with_attachments(self, user_id: int, limit: int = 100) -> List[Dict]:
        """
        Get emails that have attachments.

        Args:
            user_id: User ID
            limit: Maximum results

        Returns:
            List of emails with attachments
        """
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM emails
                WHERE user_id = ? AND (
                    has_attachments = 1 OR
                    id IN (SELECT DISTINCT email_id FROM attachments)
                )
                ORDER BY received_at DESC
                LIMIT ?
            """, (user_id, limit))

            return [dict(row) for row in cursor.fetchall()]

        finally:
            conn.close()

    def get_attachment_statistics(self, user_id: int) -> Dict:
        """
        Get statistics about user's attachments.

        Args:
            user_id: User ID

        Returns:
            Dictionary with statistics
        """
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()

            # Total attachments
            cursor.execute("""
                SELECT COUNT(*) as count FROM attachments a
                JOIN emails e ON a.email_id = e.id
                WHERE e.user_id = ?
            """, (user_id,))
            total = cursor.fetchone()['count']

            # Total size
            cursor.execute("""
                SELECT SUM(size_bytes) as total_size FROM attachments a
                JOIN emails e ON a.email_id = e.id
                WHERE e.user_id = ?
            """, (user_id,))
            total_size = cursor.fetchone()['total_size'] or 0

            # By type
            cursor.execute("""
                SELECT mime_type, COUNT(*) as count FROM attachments a
                JOIN emails e ON a.email_id = e.id
                WHERE e.user_id = ?
                GROUP BY mime_type
                ORDER BY count DESC
            """, (user_id,))
            by_type = {row['mime_type']: row['count'] for row in cursor.fetchall()}

            return {
                'total_attachments': total,
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'by_type': by_type
            }

        finally:
            conn.close()
