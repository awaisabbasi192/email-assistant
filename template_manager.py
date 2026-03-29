"""Template management for reply generation."""

import logging
from typing import Dict, List, Optional
from database import DatabaseManager

logger = logging.getLogger(__name__)


class TemplateManager:
    """Manages reply templates."""

    DEFAULT_TEMPLATES = {
        "Quick Acknowledgment": {
            "category": "work",
            "body": "Hi [SENDER_NAME],\n\nThank you for your email. I've received your message and will get back to you soon.\n\nBest regards"
        },
        "Help Needed Response": {
            "category": "support",
            "body": "Hi [SENDER_NAME],\n\nThank you for reaching out for help. I appreciate your question and will provide a detailed response shortly.\n\nBest regards"
        },
        "Feedback Appreciation": {
            "category": "work",
            "body": "Hi [SENDER_NAME],\n\nThank you for sharing your feedback. Your input is valuable, and I appreciate you taking the time to reach out.\n\nBest regards"
        },
        "Meeting Request": {
            "category": "work",
            "body": "Hi [SENDER_NAME],\n\nThank you for your meeting request. I'm interested in discussing this further. Let me check my schedule and get back to you with available times.\n\nBest regards"
        },
        "Personal Catch-up": {
            "category": "personal",
            "body": "Hi [SENDER_NAME],\n\nGreat to hear from you! Thanks for reaching out. I'd love to catch up soon.\n\nBest regards"
        },
        "Newsletter Response": {
            "category": "newsletter",
            "body": "Hi,\n\nThank you for the newsletter. I appreciate you keeping me informed.\n\nBest regards"
        },
        "Payment Confirmation": {
            "category": "bills",
            "body": "Hi,\n\nThank you for the payment confirmation. I appreciate your business.\n\nBest regards"
        }
    }

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        """
        Initialize template manager.

        Args:
            db_manager: DatabaseManager instance
        """
        self.db = db_manager or DatabaseManager()
        self.init_default_templates()

    def init_default_templates(self) -> None:
        """Initialize default templates in database."""
        for name, template_data in self.DEFAULT_TEMPLATES.items():
            existing = self.db.get_all_templates()
            if not any(t['name'] == name for t in existing):
                self.db.add_template(
                    name=name,
                    body=template_data['body'],
                    category=template_data['category'],
                    variables=["SENDER_NAME"]
                )
                logger.info(f"Initialized template: {name}")

    def get_template(self, template_id: int) -> Optional[Dict]:
        """Get template by ID."""
        return self.db.get_template(template_id)

    def get_all_templates(self) -> List[Dict]:
        """Get all templates."""
        return self.db.get_all_templates()

    def get_templates_by_category(self, category: str) -> List[Dict]:
        """Get templates for a category."""
        return self.db.get_templates_by_category(category)

    def add_template(self, name: str, body: str, category: Optional[str] = None,
                     variables: Optional[List[str]] = None) -> int:
        """Add custom template."""
        template_id = self.db.add_template(name, body, category, variables)
        if template_id > 0:
            logger.info(f"Added template: {name}")
        return template_id

    def apply_template(self, template: Dict, variables: Optional[Dict[str, str]] = None) -> str:
        """
        Apply template with variable substitution.

        Args:
            template: Template dictionary
            variables: Dictionary of variable names to values

        Returns:
            Rendered template text
        """
        body = template['body']
        variables = variables or {}

        # Replace variables
        for var_name, var_value in variables.items():
            placeholder = f"[{var_name}]"
            body = body.replace(placeholder, var_value)

        return body

    def suggest_template(self, email_data: Dict, category: str) -> Optional[Dict]:
        """
        Suggest a template based on email content and category.

        Args:
            email_data: Email data
            category: Email category

        Returns:
            Suggested template or None
        """
        templates = self.get_templates_by_category(category)

        if not templates:
            return None

        # Return most-used template for category
        return max(templates, key=lambda t: t['usage_count']) if templates else None

    def render_template(self, template_id: int, email_data: Dict) -> Optional[str]:
        """
        Render template with email data.

        Args:
            template_id: Template ID
            email_data: Email data with 'sender' field

        Returns:
            Rendered template
        """
        template = self.get_template(template_id)
        if not template:
            return None

        # Extract sender name
        sender = email_data.get('sender', 'there')
        if '<' in sender:
            sender_name = sender.split('<')[0].strip('"').strip()
        else:
            sender_name = sender.split('@')[0] if '@' in sender else sender

        variables = {
            'SENDER_NAME': sender_name
        }

        rendered = self.apply_template(template, variables)

        # Mark as used
        self.db.increment_template_usage(template_id)

        return rendered

    def get_template_suggestions(self, category: str, limit: int = 3) -> List[Dict]:
        """Get suggested templates for category."""
        templates = self.get_templates_by_category(category)
        # Sort by usage count (most used first)
        sorted_templates = sorted(templates, key=lambda t: t['usage_count'], reverse=True)
        return sorted_templates[:limit]
