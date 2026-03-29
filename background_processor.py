"""Background email processor for multi-user support using APScheduler."""

import logging
import threading
from datetime import datetime
from typing import Optional

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)


class MultiUserEmailProcessor:
    """Background processor for handling emails from all users."""

    def __init__(self, db_manager, gmail_auth, reply_generator):
        """
        Initialize multi-user email processor.

        Args:
            db_manager: DatabaseManager instance
            gmail_auth: MultiUserGmailAuthenticator instance
            reply_generator: Reply generation module (Ollama or Claude)
        """
        self.db = db_manager
        self.gmail_auth = gmail_auth
        self.reply_generator = reply_generator
        self.scheduler = BackgroundScheduler()
        self.is_running = False
        self.lock = threading.Lock()

    def start(self, check_interval_seconds: int = 60):
        """
        Start background email processing.

        Args:
            check_interval_seconds: Interval between email checks (default 60 seconds)
        """
        if self.is_running:
            logger.warning("Background processor already running")
            return

        try:
            # Schedule job
            self.scheduler.add_job(
                self.process_all_users,
                trigger=IntervalTrigger(seconds=check_interval_seconds),
                id='process_all_users',
                name='Process emails for all active users',
                replace_existing=True,
                max_instances=1  # Prevent concurrent job execution
            )

            # Start scheduler
            self.scheduler.start()
            self.is_running = True

            logger.info(f"Background processor started (check interval: {check_interval_seconds}s)")
            print(f"✓ Background email processor started")

        except Exception as e:
            logger.error(f"Error starting background processor: {e}")
            raise

    def stop(self):
        """Stop background email processing."""
        if not self.is_running:
            logger.warning("Background processor not running")
            return

        try:
            self.scheduler.shutdown(wait=True)
            self.is_running = False
            logger.info("Background processor stopped")
            print("✓ Background email processor stopped")

        except Exception as e:
            logger.error(f"Error stopping background processor: {e}")

    def process_all_users(self):
        """
        Process emails for all active users with Gmail connected.

        This is called periodically by APScheduler.
        """
        try:
            # Get all active users with Gmail connected
            users = self.db.get_active_users_with_gmail()

            if not users:
                logger.debug("No active users with Gmail connected")
                return

            logger.info(f"Processing emails for {len(users)} user(s)")

            for user in users:
                try:
                    self.process_user_emails(user['id'], user['username'], user['gmail_email'])

                except Exception as e:
                    # Isolate errors per user - don't let one user's error affect others
                    logger.error(f"Error processing emails for user {user['id']} ({user['username']}): {e}")
                    continue

        except Exception as e:
            logger.error(f"Error in process_all_users: {e}")

    def process_user_emails(self, user_id: int, username: str, gmail_email: str):
        """
        Process emails for a single user.

        Args:
            user_id: User ID
            username: Username (for logging)
            gmail_email: User's Gmail email address (for logging)
        """
        try:
            logger.debug(f"Processing emails for user {user_id} ({username})")

            # Get Gmail service for user
            gmail_service = self.gmail_auth.get_user_gmail_service(user_id)

            if not gmail_service:
                logger.warning(f"Could not get Gmail service for user {user_id}")
                return

            # Fetch unread emails
            from email_processor import EmailProcessor

            processor = EmailProcessor(gmail_service, self.db)
            emails = processor.get_unread_emails(
                max_results=5,  # Process max 5 emails at a time
                exclude_labels=['SENT', 'DRAFT', 'SPAM', 'TRASH'],
                skip_keywords=['noreply', 'no-reply', 'notification', 'alert', 'bot@']
            )

            if not emails:
                logger.debug(f"No unread emails for user {user_id}")
                return

            logger.info(f"Found {len(emails)} unread emails for user {user_id}")

            # Process each email
            processed_count = 0

            for email in emails:
                try:
                    # Generate reply
                    reply_body = self.reply_generator.generate_reply(email)

                    if not reply_body:
                        logger.warning(f"Failed to generate reply for email from {email['sender']}")
                        continue

                    # Create draft
                    draft_id = processor.create_draft_with_reply_headers(email, reply_body)

                    if not draft_id:
                        logger.warning(f"Failed to create draft for email from {email['sender']}")
                        continue

                    # Store in database
                    email_id = self.db.add_email(
                        user_id=user_id,
                        message_id=email['message_id'],
                        sender=email['sender'],
                        subject=email['subject'],
                        body=email['body'][:1000]
                    )

                    draft_record_id = self.db.add_draft(
                        user_id=user_id,
                        email_id=email_id,
                        reply_body=reply_body,
                        model_used=getattr(self.reply_generator, 'model_name', 'unknown'),
                        confidence_score=0.85
                    )

                    # Mark as processed
                    self.db.mark_email_processed(email_id)

                    # Mark as read
                    try:
                        processor.mark_as_read(email['message_id'])
                    except Exception as e:
                        logger.warning(f"Could not mark email as read: {e}")

                    processed_count += 1
                    logger.debug(f"Processed email from {email['sender']} for user {user_id}")

                except Exception as e:
                    logger.error(f"Error processing individual email for user {user_id}: {e}")
                    continue

            logger.info(f"Processed {processed_count} emails for user {user_id} ({username})")

        except Exception as e:
            logger.error(f"Error processing emails for user {user_id}: {e}")
            raise

    def is_healthy(self) -> bool:
        """Check if background processor is running and healthy."""
        return self.is_running and self.scheduler.running


# Global background processor instance
_processor = None


def get_background_processor():
    """Get or create global background processor instance."""
    global _processor
    return _processor


def set_background_processor(processor: MultiUserEmailProcessor):
    """Set global background processor instance."""
    global _processor
    _processor = processor
