"""Auto email processor - simple background worker without signal issues."""

import time
import logging
import requests
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


class SimpleEmailProcessor:
    """Simple email processor that avoids signal handling issues."""

    def __init__(self, config: dict):
        """Initialize processor."""
        self.config = config
        self.check_interval = config.get('gmail', {}).get('check_interval_seconds', 60)
        self.max_results = config.get('gmail', {}).get('max_results', 3)
        self.running = True
        logger.info("SimpleEmailProcessor initialized")

    def run(self):
        """Run processor in loop."""
        logger.info(f"Auto processor starting - checks every {self.check_interval}s")

        while self.running:
            try:
                self.check_and_process()
                time.sleep(self.check_interval)
            except KeyboardInterrupt:
                logger.info("Processor stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in processor loop: {e}")
                time.sleep(5)

    def check_and_process(self):
        """Check for new emails and process them."""
        try:
            from email_processor import EmailProcessor
            from database import DatabaseManager
            from email_classifier import EmailClassifier
            from googleapiclient.discovery import build
            from google.oauth2.credentials import Credentials
            import os

            # Load credentials
            token_file = 'token.json'
            if not os.path.exists(token_file):
                logger.debug("No Gmail token found - skipping email check")
                return

            creds = Credentials.from_authorized_user_file(token_file)
            if not creds.valid:
                return

            # Create services
            service = build('gmail', 'v1', credentials=creds)
            processor = EmailProcessor(service)
            db = DatabaseManager()
            classifier = EmailClassifier()

            # Fetch unread emails
            emails = processor.get_unread_emails(max_results=self.max_results)

            if not emails:
                logger.debug("No new emails")
                return

            logger.info(f"Processing {len(emails)} new emails")

            # Classify each email
            for email in emails:
                try:
                    email_id = email.get('email_id')
                    if not email_id:
                        continue

                    # Classify
                    category, confidence = classifier.classify_email(email)
                    priority = classifier.score_priority(email)

                    # Update database
                    db.update_email_category(email_id, category)
                    db.update_email_priority(email_id, priority)

                    # Try to generate draft
                    try:
                        self._generate_draft(email, db)
                    except Exception as e:
                        logger.debug(f"Could not generate draft: {e}")

                    logger.debug(f"Processed email {email_id}: {category} / {priority}")

                except Exception as e:
                    logger.error(f"Error processing individual email: {e}")

        except Exception as e:
            logger.error(f"Error in check_and_process: {e}")

    def _generate_draft(self, email: dict, db) -> Optional[int]:
        """Generate AI draft for email."""
        try:
            email_id = email.get('email_id')
            sender = email.get('sender', '')
            subject = email.get('subject', '')
            body = email.get('body', '')

            # Check existing drafts
            existing = db.get_drafts_by_email(email_id)
            if existing:
                return existing[0]['id']

            # Generate with Ollama
            prompt = f"""Generate a professional, concise email reply.

From: {sender}
Subject: {subject}
Body: {body}

Reply:"""

            response = requests.post(
                'http://127.0.0.1:11434/api/generate',
                json={
                    'model': 'mistral',
                    'prompt': prompt,
                    'stream': False
                },
                timeout=30
            )

            if response.status_code == 200:
                reply = response.json().get('response', '').strip()
                if reply:
                    draft_id = db.add_draft(email_id, reply, model_used='mistral')
                    logger.debug(f"Generated draft {draft_id} for email {email_id}")
                    return draft_id

        except requests.exceptions.RequestException:
            logger.debug("Ollama not available for draft generation")
        except Exception as e:
            logger.debug(f"Draft generation error: {e}")

        # Fallback: create template draft
        try:
            template_reply = "Thank you for your email. I will review and respond shortly."
            draft_id = db.add_draft(email_id, template_reply, model_used='template')
            return draft_id
        except Exception as e:
            logger.error(f"Error creating template draft: {e}")

        return None

    def stop(self):
        """Stop processor."""
        self.running = False
        logger.info("Processor stopping...")


if __name__ == '__main__':
    import json
    from pathlib import Path

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    config_file = Path('config.json')
    if config_file.exists():
        with open(config_file) as f:
            config = json.load(f)

        processor = SimpleEmailProcessor(config)
        processor.run()
