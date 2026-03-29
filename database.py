"""SQLite database management for email assistant."""

import sqlite3
import json
import logging
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

DB_FILE = "email_assistant.db"


class DatabaseManager:
    """Manages SQLite database operations."""

    def __init__(self, db_file: str = DB_FILE, default_user_id: int = 1):
        """
        Initialize database manager.

        Args:
            db_file: Path to SQLite database file
            default_user_id: Default user ID for single-user mode (backward compatibility)
        """
        self.db_file = db_file
        self.default_user_id = default_user_id
        self.init_database()
        self._ensure_default_user()

    def get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn

    @contextmanager
    def get_connection_context(self):
        """
        Context manager for database connections.

        Ensures connections are properly committed and closed even on exceptions.
        """
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database transaction rolled back due to error: {e}")
            raise
        finally:
            conn.close()

    def _ensure_default_user(self) -> None:
        """Ensure default user exists for single-user mode."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE id = ?", (self.default_user_id,))
            if cursor.fetchone() is None:
                # Default user doesn't exist, create it
                cursor.execute("""
                    INSERT INTO users (id, username, email, password_hash, gmail_connected)
                    VALUES (?, ?, ?, ?, ?)
                """, (self.default_user_id, 'default_user', 'user@example.com', 'placeholder_hash', 0))
                conn.commit()
                logger.info(f"Created default user with ID {self.default_user_id}")
        except sqlite3.Error as e:
            logger.warning(f"Could not ensure default user exists: {e}")
        finally:
            conn.close()

    def init_database(self) -> None:
        """Initialize database schema."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Create users table (MULTI-USER SUPPORT)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    gmail_connected BOOLEAN DEFAULT 0,
                    gmail_email TEXT
                )
            """)

            # Create oauth_tokens table for storing encrypted Gmail tokens
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS oauth_tokens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    service TEXT DEFAULT 'gmail',
                    token_data TEXT NOT NULL,
                    expires_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)

            # Create emails table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS emails (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    message_id TEXT NOT NULL,
                    sender TEXT NOT NULL,
                    subject TEXT,
                    body TEXT,
                    received_at TIMESTAMP,
                    category TEXT,
                    priority TEXT DEFAULT 'normal',
                    is_read BOOLEAN DEFAULT 0,
                    is_processed BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    UNIQUE(user_id, message_id)
                )
            """)

            # Create drafts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS drafts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    email_id INTEGER NOT NULL,
                    reply_body TEXT,
                    model_used TEXT DEFAULT 'mistral',
                    status TEXT DEFAULT 'pending',
                    confidence_score REAL,
                    edited BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (email_id) REFERENCES emails(id)
                )
            """)

            # Create draft edits table for version tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS draft_edits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    draft_id INTEGER NOT NULL,
                    previous_body TEXT,
                    new_body TEXT,
                    edited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (draft_id) REFERENCES drafts(id)
                )
            """)

            # Create templates table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    name TEXT NOT NULL,
                    category TEXT,
                    body TEXT NOT NULL,
                    variables TEXT,
                    usage_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    UNIQUE(user_id, name)
                )
            """)

            # Create settings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    description TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create analytics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    date DATE NOT NULL,
                    total_emails INTEGER DEFAULT 0,
                    processed_emails INTEGER DEFAULT 0,
                    category_distribution TEXT,
                    avg_response_time REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    UNIQUE(user_id, date)
                )
            """)

            # Create indexes for performance (MULTI-USER)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_emails_user_id ON emails(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_emails_message_id ON emails(message_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_emails_category ON emails(category)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_emails_created_at ON emails(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_drafts_user_id ON drafts(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_drafts_email_id ON drafts(email_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_drafts_status ON drafts(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_templates_user_id ON templates(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_analytics_user_id ON analytics(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_analytics_date ON analytics(date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_oauth_tokens_user_id ON oauth_tokens(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_oauth_tokens_service ON oauth_tokens(service)")

            conn.commit()
            logger.info("Database initialized successfully")

        except sqlite3.Error as e:
            logger.error(f"Error initializing database: {e}")
            raise
        finally:
            conn.close()

    # ===== USER OPERATIONS =====

    def add_user(self, username: str, email: str, password_hash: str) -> Optional[int]:
        """
        Add new user to database.

        Args:
            username: Username
            email: User email
            password_hash: Bcrypt hashed password

        Returns:
            User ID or None if failed
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO users (username, email, password_hash)
                VALUES (?, ?, ?)
            """, (username, email, password_hash))

            conn.commit()
            user_id = cursor.lastrowid
            logger.info(f"Added user: {username}")
            return user_id

        except sqlite3.IntegrityError as e:
            logger.warning(f"User registration failed: {e}")
            return None
        except sqlite3.Error as e:
            logger.error(f"Error adding user: {e}")
            raise
        finally:
            conn.close()

    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def update_user_last_login(self, user_id: int) -> bool:
        """Update user's last login timestamp."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE users
                SET last_login = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (user_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def update_user_gmail_status(self, user_id: int, gmail_connected: bool, gmail_email: Optional[str] = None) -> bool:
        """Update user's Gmail connection status."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE users
                SET gmail_connected = ?, gmail_email = ?
                WHERE id = ?
            """, (1 if gmail_connected else 0, gmail_email, user_id))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def get_active_users_with_gmail(self) -> List[Dict]:
        """Get all active users who have Gmail connected."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT * FROM users
                WHERE is_active = 1 AND gmail_connected = 1
                ORDER BY last_login DESC
            """)
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    # ===== OAUTH TOKEN OPERATIONS =====

    def store_oauth_token(self, user_id: int, token_data: str, expires_at: Optional[str] = None, service: str = 'gmail') -> int:
        """
        Store encrypted OAuth token for user.

        Args:
            user_id: User ID
            token_data: Encrypted token JSON
            expires_at: Token expiry timestamp
            service: OAuth service (gmail, outlook, etc.)

        Returns:
            OAuth token record ID
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO oauth_tokens (user_id, service, token_data, expires_at)
                VALUES (?, ?, ?, ?)
            """, (user_id, service, token_data, expires_at))

            conn.commit()
            return cursor.lastrowid

        except sqlite3.Error as e:
            logger.error(f"Error storing OAuth token: {e}")
            raise
        finally:
            conn.close()

    def get_oauth_token(self, user_id: int, service: str = 'gmail') -> Optional[Dict]:
        """Get OAuth token for user."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT * FROM oauth_tokens
                WHERE user_id = ? AND service = ?
            """, (user_id, service))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def delete_oauth_token(self, user_id: int, service: str = 'gmail') -> bool:
        """Delete OAuth token for user."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                DELETE FROM oauth_tokens
                WHERE user_id = ? AND service = ?
            """, (user_id, service))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    # ===== EMAIL OPERATIONS =====

    def add_email(self, user_id: int, message_id: str, sender: str, subject: str, body: str,
                  received_at: Optional[str] = None, category: Optional[str] = None) -> int:
        """
        Add email to database.

        Args:
            user_id: User ID (MULTI-USER)
            message_id: Gmail message ID
            sender: Email sender
            subject: Email subject
            body: Email body
            received_at: Email received timestamp
            category: Email category

        Returns:
            Email ID
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO emails (user_id, message_id, sender, subject, body, received_at, category)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, message_id, sender, subject, body, received_at or datetime.now().isoformat(), category))

            conn.commit()
            email_id = cursor.lastrowid
            logger.debug(f"Added email {email_id} from {sender}")
            return email_id

        except sqlite3.IntegrityError:
            logger.debug(f"Email {message_id} already exists in database")
            return self.get_email_by_message_id(message_id)['id']
        except sqlite3.Error as e:
            logger.error(f"Error adding email: {e}")
            raise
        finally:
            conn.close()

    def get_email(self, email_id: int) -> Optional[Dict]:
        """Get email by ID."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM emails WHERE id = ?", (email_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def get_email_by_message_id(self, message_id: str) -> Optional[Dict]:
        """Get email by Gmail message ID."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM emails WHERE message_id = ?", (message_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def get_all_emails(self, user_id: int, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Get all emails for user with pagination."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT * FROM emails
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """, (user_id, limit, offset))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def get_emails_by_category(self, user_id: int, category: str, limit: int = 100) -> List[Dict]:
        """Get emails by category for user."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT * FROM emails
                WHERE user_id = ? AND category = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (user_id, category, limit))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def update_email_category(self, email_id: int, category: str) -> bool:
        """Update email category."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE emails
                SET category = ?
                WHERE id = ?
            """, (category, email_id))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def mark_email_processed(self, email_id: int) -> bool:
        """Mark email as processed."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE emails
                SET is_processed = 1
                WHERE id = ?
            """, (email_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    # ===== DRAFT OPERATIONS =====

    def add_draft(self, user_id: int, email_id: int, reply_body: str, model_used: str = "mistral",
                  confidence_score: Optional[float] = None) -> int:
        """
        Add draft to database.

        Args:
            user_id: User ID (MULTI-USER)
            email_id: Email ID
            reply_body: Draft reply text
            model_used: LLM model used
            confidence_score: Confidence score of reply

        Returns:
            Draft ID
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO drafts (user_id, email_id, reply_body, model_used, confidence_score)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, email_id, reply_body, model_used, confidence_score))

            conn.commit()
            draft_id = cursor.lastrowid
            logger.debug(f"Added draft {draft_id} for email {email_id}")
            return draft_id

        except sqlite3.Error as e:
            logger.error(f"Error adding draft: {e}")
            raise
        finally:
            conn.close()

    def get_draft(self, draft_id: int) -> Optional[Dict]:
        """Get draft by ID."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM drafts WHERE id = ?", (draft_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def get_drafts_by_email(self, email_id: int) -> List[Dict]:
        """Get all drafts for an email."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT * FROM drafts
                WHERE email_id = ?
                ORDER BY created_at DESC
            """, (email_id,))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def get_pending_drafts(self, user_id: int, limit: int = 100) -> List[Dict]:
        """Get all pending drafts for user review."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT d.*, e.sender, e.subject, e.body
                FROM drafts d
                JOIN emails e ON d.email_id = e.id
                WHERE d.user_id = ? AND d.status = 'pending'
                ORDER BY d.created_at DESC
                LIMIT ?
            """, (user_id, limit))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def update_draft(self, draft_id: int, reply_body: str) -> bool:
        """Update draft reply body."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Get old body for edit tracking
            old_draft = self.get_draft(draft_id)
            if old_draft:
                cursor.execute("""
                    INSERT INTO draft_edits (draft_id, previous_body, new_body)
                    VALUES (?, ?, ?)
                """, (draft_id, old_draft['reply_body'], reply_body))

            # Update draft
            cursor.execute("""
                UPDATE drafts
                SET reply_body = ?, edited = 1, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (reply_body, draft_id))

            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def update_draft_status(self, draft_id: int, status: str) -> bool:
        """Update draft status (pending/approved/sent/deleted)."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE drafts
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (status, draft_id))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def get_draft_edit_history(self, draft_id: int) -> List[Dict]:
        """Get edit history for a draft."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT * FROM draft_edits
                WHERE draft_id = ?
                ORDER BY edited_at
            """, (draft_id,))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    # ===== TEMPLATE OPERATIONS =====

    def add_template(self, user_id: int, name: str, body: str, category: Optional[str] = None,
                     variables: Optional[List[str]] = None) -> int:
        """Add reply template for user."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            variables_json = json.dumps(variables or [])
            cursor.execute("""
                INSERT INTO templates (user_id, name, category, body, variables)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, name, category, body, variables_json))

            conn.commit()
            logger.info(f"Added template: {name}")
            return cursor.lastrowid

        except sqlite3.IntegrityError:
            logger.warning(f"Template {name} already exists")
            return -1
        finally:
            conn.close()

    def get_template(self, template_id: int) -> Optional[Dict]:
        """Get template by ID."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM templates WHERE id = ?", (template_id,))
            row = cursor.fetchone()
            if row:
                result = dict(row)
                result['variables'] = json.loads(result['variables'])
                return result
            return None
        finally:
            conn.close()

    def get_all_templates(self, user_id: int) -> List[Dict]:
        """Get all templates for user."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM templates WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
            templates = []
            for row in cursor.fetchall():
                result = dict(row)
                result['variables'] = json.loads(result['variables'])
                templates.append(result)
            return templates
        finally:
            conn.close()

    def get_templates_by_category(self, category: str) -> List[Dict]:
        """Get templates by category."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT * FROM templates
                WHERE category = ?
                ORDER BY usage_count DESC
            """, (category,))
            templates = []
            for row in cursor.fetchall():
                result = dict(row)
                result['variables'] = json.loads(result['variables'])
                templates.append(result)
            return templates
        finally:
            conn.close()

    def increment_template_usage(self, template_id: int) -> bool:
        """Increment template usage count."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE templates
                SET usage_count = usage_count + 1
                WHERE id = ?
            """, (template_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    # ===== ANALYTICS OPERATIONS =====

    def add_analytics(self, user_id: int, date: str, total_emails: int, processed_emails: int,
                      category_distribution: Optional[Dict] = None) -> int:
        """Add daily analytics for user."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            dist_json = json.dumps(category_distribution or {})
            cursor.execute("""
                INSERT OR REPLACE INTO analytics (user_id, date, total_emails, processed_emails, category_distribution)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, date, total_emails, processed_emails, dist_json))

            conn.commit()
            return cursor.lastrowid

        except sqlite3.Error as e:
            logger.error(f"Error adding analytics: {e}")
            raise
        finally:
            conn.close()

    def get_analytics(self, user_id: int, date: str) -> Optional[Dict]:
        """Get analytics for a specific date for user."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM analytics WHERE user_id = ? AND date = ?", (user_id, date))
            row = cursor.fetchone()
            if row:
                result = dict(row)
                result['category_distribution'] = json.loads(result['category_distribution'])
                return result
            return None
        finally:
            conn.close()

    def get_analytics_range(self, user_id: int, start_date: str, end_date: str) -> List[Dict]:
        """Get analytics for a date range for user."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT * FROM analytics
                WHERE user_id = ? AND date BETWEEN ? AND ?
                ORDER BY date
            """, (user_id, start_date, end_date))
            analytics = []
            for row in cursor.fetchall():
                result = dict(row)
                result['category_distribution'] = json.loads(result['category_distribution'])
                analytics.append(result)
            return analytics
        finally:
            conn.close()

    # ===== STATISTICS =====

    def get_email_count(self, user_id: int) -> int:
        """Get email count for user."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT COUNT(*) as count FROM emails WHERE user_id = ?", (user_id,))
            return cursor.fetchone()['count']
        finally:
            conn.close()

    def get_processed_count(self, user_id: int) -> int:
        """Get count of processed emails for user."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT COUNT(*) as count FROM emails WHERE user_id = ? AND is_processed = 1", (user_id,))
            return cursor.fetchone()['count']
        finally:
            conn.close()

    def get_draft_count(self, user_id: int, status: Optional[str] = None) -> int:
        """Get count of drafts for user."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            if status:
                cursor.execute("SELECT COUNT(*) as count FROM drafts WHERE user_id = ? AND status = ?", (user_id, status))
            else:
                cursor.execute("SELECT COUNT(*) as count FROM drafts WHERE user_id = ?", (user_id,))
            return cursor.fetchone()['count']
        finally:
            conn.close()

    def get_category_distribution(self, user_id: int) -> Dict[str, int]:
        """Get distribution of emails by category for user."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT category, COUNT(*) as count
                FROM emails
                WHERE user_id = ? AND category IS NOT NULL
                GROUP BY category
            """, (user_id,))
            return {row['category']: row['count'] for row in cursor.fetchall()}
        finally:
            conn.close()

    # ===== SEARCH OPERATIONS =====

    def search_emails(self, user_id: int, search_term: str, limit: int = 100) -> List[Dict]:
        """
        Search emails by subject, sender, or body content for user.

        Args:
            user_id: User ID (MULTI-USER)
            search_term: Search term
            limit: Maximum results

        Returns:
            List of matching emails
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            query_param = f"%{search_term}%"
            cursor.execute("""
                SELECT * FROM emails
                WHERE user_id = ? AND (subject LIKE ? OR sender LIKE ? OR body LIKE ?)
                ORDER BY created_at DESC
                LIMIT ?
            """, (user_id, query_param, query_param, query_param, limit))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def search_emails_advanced(self, user_id: int, subject: Optional[str] = None,
                              sender: Optional[str] = None,
                              category: Optional[str] = None,
                              priority: Optional[str] = None,
                              is_processed: Optional[bool] = None,
                              limit: int = 100) -> List[Dict]:
        """
        Advanced search with multiple filters for user.

        Args:
            user_id: User ID (MULTI-USER)
            subject: Subject filter
            sender: Sender filter
            category: Category filter
            priority: Priority filter
            is_processed: Processing status filter
            limit: Maximum results

        Returns:
            List of matching emails
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            query = "SELECT * FROM emails WHERE user_id = ?"
            params = [user_id]

            if subject:
                query += " AND subject LIKE ?"
                params.append(f"%{subject}%")

            if sender:
                query += " AND sender LIKE ?"
                params.append(f"%{sender}%")

            if category:
                query += " AND category = ?"
                params.append(category)

            if priority:
                query += " AND priority = ?"
                params.append(priority)

            if is_processed is not None:
                query += " AND is_processed = ?"
                params.append(1 if is_processed else 0)

            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    # ===== EXPORT OPERATIONS =====

    def export_emails_to_csv(self, filepath: str, limit: Optional[int] = None) -> bool:
        """
        Export emails to CSV file.

        Args:
            filepath: Output file path
            limit: Maximum emails to export (None for all)

        Returns:
            True if successful
        """
        try:
            import csv
            emails = self.get_all_emails(limit=limit or 100000, offset=0)

            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['id', 'sender', 'subject', 'category', 'priority', 'is_processed', 'created_at'])
                writer.writeheader()
                for email in emails:
                    writer.writerow({
                        'id': email['id'],
                        'sender': email['sender'],
                        'subject': email['subject'],
                        'category': email['category'],
                        'priority': email['priority'],
                        'is_processed': email['is_processed'],
                        'created_at': email['created_at']
                    })

            logger.info(f"Exported {len(emails)} emails to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            return False

    def export_emails_to_json(self, filepath: str, limit: Optional[int] = None) -> bool:
        """
        Export emails to JSON file.

        Args:
            filepath: Output file path
            limit: Maximum emails to export (None for all)

        Returns:
            True if successful
        """
        try:
            emails = self.get_all_emails(limit=limit or 100000, offset=0)
            emails_list = []
            for email in emails:
                email_dict = dict(email)
                emails_list.append(email_dict)

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(emails_list, f, indent=2, default=str)

            logger.info(f"Exported {len(emails)} emails to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")
            return False

    # ===== CLEANUP OPERATIONS =====

    def delete_email(self, email_id: int) -> bool:
        """Delete an email."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM emails WHERE id = ?", (email_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def delete_emails_by_category(self, category: str) -> int:
        """Delete all emails in a category."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM emails WHERE category = ?", (category,))
            conn.commit()
            logger.info(f"Deleted {cursor.rowcount} emails from category {category}")
            return cursor.rowcount
        finally:
            conn.close()

    def mark_email_as_read(self, email_id: int) -> bool:
        """Mark email as read."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("UPDATE emails SET is_read = 1 WHERE id = ?", (email_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def update_email_priority(self, email_id: int, priority: str) -> bool:
        """Update email priority."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("UPDATE emails SET priority = ? WHERE id = ?", (priority, email_id))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    # ===== STATISTICS =====

    def get_statistics(self, user_id: int) -> Dict:
        """Get comprehensive statistics for user."""
        return {
            'total_emails': self.get_email_count(user_id),
            'processed_emails': self.get_processed_count(user_id),
            'pending_drafts': self.get_draft_count(user_id, 'pending'),
            'approved_drafts': self.get_draft_count(user_id, 'approved'),
            'sent_drafts': self.get_draft_count(user_id, 'sent'),
            'category_distribution': self.get_category_distribution(user_id)
        }
