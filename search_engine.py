"""Advanced email search with full-text and filtering support."""

import logging
import json
from typing import List, Dict, Optional
from datetime import datetime
from database import DatabaseManager

logger = logging.getLogger(__name__)


class EmailSearchEngine:
    """Advanced email search with full-text and complex filtering."""

    def __init__(self, db: DatabaseManager):
        """
        Initialize search engine.

        Args:
            db: DatabaseManager instance
        """
        self.db = db
        self.logger = logging.getLogger(__name__)

    def full_text_search(self, user_id: int, query: str, limit: int = 100) -> List[Dict]:
        """
        Full-text search across email content using LIKE queries.

        Args:
            user_id: User ID
            query: Search query (simple text search)
            limit: Maximum results to return

        Returns:
            List of matching emails, sorted by relevance
        """
        if not query or not query.strip():
            return []

        query_lower = query.lower().strip()

        # Split query into words for better matching
        keywords = query_lower.split()

        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()

            # Build dynamic query with OR conditions for multiple keywords
            conditions = []
            params = [user_id]

            for keyword in keywords:
                keyword_pattern = f"%{keyword}%"
                conditions.append("""(
                    LOWER(subject) LIKE ? OR
                    LOWER(sender) LIKE ? OR
                    LOWER(body) LIKE ?
                )""")
                params.extend([keyword_pattern, keyword_pattern, keyword_pattern])

            where_clause = " OR ".join(conditions)

            query_sql = f"""
                SELECT * FROM emails
                WHERE user_id = ? AND ({where_clause})
                ORDER BY received_at DESC
                LIMIT ?
            """
            params.append(limit)

            cursor.execute(query_sql, params)
            results = [dict(row) for row in cursor.fetchall()]

            self.logger.info(f"Full-text search for '{query}' returned {len(results)} results")
            return results

        finally:
            conn.close()

    def advanced_search(self, user_id: int, filters: Dict) -> List[Dict]:
        """
        Advanced search with multiple filters.

        Supported filters:
            - subject: Text to search in subject
            - sender: Sender email/name pattern
            - body: Text to search in body
            - category: Email category (work, personal, etc.)
            - priority: Email priority (low, normal, high, urgent)
            - date_from: Start date (YYYY-MM-DD)
            - date_to: End date (YYYY-MM-DD)
            - is_read: Boolean (true/false)
            - is_processed: Boolean (true/false)
            - has_attachment: Boolean (true/false)
            - limit: Maximum results

        Args:
            user_id: User ID
            filters: Dictionary of filter parameters

        Returns:
            List of emails matching all filters
        """
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()

            # Build dynamic query
            where_clauses = ["user_id = ?"]
            params = [user_id]

            # Subject filter
            if filters.get('subject'):
                where_clauses.append("LOWER(subject) LIKE ?")
                params.append(f"%{filters['subject'].lower()}%")

            # Sender filter
            if filters.get('sender'):
                where_clauses.append("LOWER(sender) LIKE ?")
                params.append(f"%{filters['sender'].lower()}%")

            # Body filter
            if filters.get('body'):
                where_clauses.append("LOWER(body) LIKE ?")
                params.append(f"%{filters['body'].lower()}%")

            # Category filter
            if filters.get('category'):
                where_clauses.append("category = ?")
                params.append(filters['category'])

            # Priority filter
            if filters.get('priority'):
                where_clauses.append("priority = ?")
                params.append(filters['priority'])

            # Date range filters
            if filters.get('date_from'):
                where_clauses.append("received_at >= ?")
                params.append(f"{filters['date_from']}T00:00:00")

            if filters.get('date_to'):
                where_clauses.append("received_at <= ?")
                params.append(f"{filters['date_to']}T23:59:59")

            # Read status filter
            if filters.get('is_read') is not None:
                where_clauses.append("is_read = ?")
                params.append(1 if filters['is_read'] else 0)

            # Processed status filter
            if filters.get('is_processed') is not None:
                where_clauses.append("is_processed = ?")
                params.append(1 if filters['is_processed'] else 0)

            # Has attachments filter
            if filters.get('has_attachment') is not None:
                where_clauses.append("has_attachments = ?")
                params.append(1 if filters['has_attachment'] else 0)

            # Build final query
            where_clause = " AND ".join(where_clauses)
            limit = filters.get('limit', 100)

            query_sql = f"""
                SELECT * FROM emails
                WHERE {where_clause}
                ORDER BY received_at DESC
                LIMIT ?
            """
            params.append(limit)

            cursor.execute(query_sql, params)
            results = [dict(row) for row in cursor.fetchall()]

            self.logger.info(f"Advanced search returned {len(results)} results")
            return results

        except Exception as e:
            self.logger.error(f"Error in advanced search: {e}")
            raise
        finally:
            conn.close()

    def save_search(self, user_id: int, name: str, filters: Dict) -> int:
        """
        Save a search query for future reuse.

        Args:
            user_id: User ID
            name: Search name (e.g., "Work Emails")
            filters: Dictionary of filter parameters

        Returns:
            Saved search ID
        """
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()

            query_json = json.dumps(filters)

            # Check if saved search table exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS saved_searches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    query_json TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_used TIMESTAMP,
                    use_count INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    UNIQUE(user_id, name)
                )
            """)

            cursor.execute("""
                INSERT OR REPLACE INTO saved_searches (user_id, name, query_json)
                VALUES (?, ?, ?)
            """, (user_id, name, query_json))

            conn.commit()
            search_id = cursor.lastrowid
            self.logger.info(f"Saved search '{name}' for user {user_id}")
            return search_id

        finally:
            conn.close()

    def get_saved_searches(self, user_id: int) -> List[Dict]:
        """
        Get all saved searches for a user.

        Args:
            user_id: User ID

        Returns:
            List of saved searches
        """
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM saved_searches
                WHERE user_id = ?
                ORDER BY last_used DESC, name ASC
            """, (user_id,))

            searches = []
            for row in cursor.fetchall():
                search = dict(row)
                search['filters'] = json.loads(search['query_json'])
                searches.append(search)

            return searches

        except Exception as e:
            self.logger.warning(f"Could not retrieve saved searches: {e}")
            return []
        finally:
            conn.close()

    def execute_saved_search(self, user_id: int, search_id: int) -> List[Dict]:
        """
        Execute a saved search by ID.

        Args:
            user_id: User ID
            search_id: Saved search ID

        Returns:
            Search results
        """
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT query_json FROM saved_searches
                WHERE id = ? AND user_id = ?
            """, (search_id, user_id))

            row = cursor.fetchone()
            if not row:
                self.logger.warning(f"Saved search {search_id} not found")
                return []

            filters = json.loads(row['query_json'])

            # Update usage stats
            cursor.execute("""
                UPDATE saved_searches
                SET last_used = CURRENT_TIMESTAMP, use_count = use_count + 1
                WHERE id = ?
            """, (search_id,))
            conn.commit()

            # Execute search
            return self.advanced_search(user_id, filters)

        finally:
            conn.close()

    def delete_saved_search(self, user_id: int, search_id: int) -> bool:
        """
        Delete a saved search.

        Args:
            user_id: User ID
            search_id: Saved search ID

        Returns:
            True if deleted, False otherwise
        """
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()

            cursor.execute("""
                DELETE FROM saved_searches
                WHERE id = ? AND user_id = ?
            """, (search_id, user_id))

            conn.commit()
            success = cursor.rowcount > 0

            if success:
                self.logger.info(f"Deleted saved search {search_id}")

            return success

        finally:
            conn.close()

    def search_by_sender(self, user_id: int, sender_pattern: str, limit: int = 50) -> List[Dict]:
        """
        Quick search by sender.

        Args:
            user_id: User ID
            sender_pattern: Sender email or name pattern
            limit: Maximum results

        Returns:
            List of emails from matching sender
        """
        return self.advanced_search(user_id, {
            'sender': sender_pattern,
            'limit': limit
        })

    def search_by_date_range(self, user_id: int, date_from: str, date_to: str, limit: int = 100) -> List[Dict]:
        """
        Quick search by date range.

        Args:
            user_id: User ID
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
            limit: Maximum results

        Returns:
            List of emails in date range
        """
        return self.advanced_search(user_id, {
            'date_from': date_from,
            'date_to': date_to,
            'limit': limit
        })

    def search_unread(self, user_id: int, limit: int = 100) -> List[Dict]:
        """
        Get unread emails.

        Args:
            user_id: User ID
            limit: Maximum results

        Returns:
            List of unread emails
        """
        return self.advanced_search(user_id, {
            'is_read': False,
            'limit': limit
        })

    def search_by_priority(self, user_id: int, priority: str, limit: int = 100) -> List[Dict]:
        """
        Get emails by priority level.

        Args:
            user_id: User ID
            priority: Priority level (low, normal, high, urgent)
            limit: Maximum results

        Returns:
            List of emails with given priority
        """
        return self.advanced_search(user_id, {
            'priority': priority,
            'limit': limit
        })

    def search_by_category(self, user_id: int, category: str, limit: int = 100) -> List[Dict]:
        """
        Get emails by category.

        Args:
            user_id: User ID
            category: Email category
            limit: Maximum results

        Returns:
            List of emails in category
        """
        return self.advanced_search(user_id, {
            'category': category,
            'limit': limit
        })
