"""Claude API integration for email reply generation."""

import logging
import os

logger = logging.getLogger(__name__)

# Try to import Claude, gracefully handle if unavailable
try:
    from anthropic import Anthropic, APIError, RateLimitError, APIConnectionError
    ANTHROPIC_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Anthropic library not available: {e}")
    logger.warning("Install with: pip install anthropic")
    ANTHROPIC_AVAILABLE = False

    # Create dummy classes for graceful degradation
    class Anthropic:
        def __init__(self, *args, **kwargs):
            raise ImportError("anthropic library not installed. Install with: pip install anthropic")

    class APIError(Exception):
        pass

    class RateLimitError(Exception):
        pass

    class APIConnectionError(Exception):
        pass


class ClaudeReplyGenerator:
    """Generates email replies using Claude API."""

    def __init__(self, model: str = "claude-3-5-sonnet-20241022", temperature: float = 0.7, max_tokens: int = 500):
        """
        Initialize Claude reply generator.

        Args:
            model: Claude model to use
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in response

        Raises:
            ImportError: If anthropic library not available
            ValueError: If API key not set
        """
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("Anthropic library not available. Install with: pip install anthropic")

        # Check for API key
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            logger.warning("ANTHROPIC_API_KEY environment variable not set")
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable not set. "
                "Set it with: export ANTHROPIC_API_KEY='sk-...'"
            )

        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        try:
            self.client = Anthropic(api_key=api_key)
            logger.info(f"Claude API initialized with model: {model}")
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic client: {e}")
            raise

    def generate_reply(self, email_data: dict, style: str = "professional") -> str:
        """
        Generate an email reply for the given email.
        Uses Claude API if available, falls back to intelligent templates if not.

        Args:
            email_data: Dictionary containing 'subject', 'sender', 'body', and 'to'
            style: Reply style (professional, friendly, brief, detailed)

        Returns:
            Generated reply text
        """
        try:
            prompt = self._create_prompt(email_data, style)

            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            reply = message.content[0].text.strip()
            logger.info(f"Generated reply using Claude for email from {email_data.get('sender', 'unknown')}")
            return reply

        except RateLimitError as e:
            logger.warning(f"Claude API rate limit exceeded: {e}")
            logger.info("Circuit breaker will switch to Ollama")
            raise  # Re-raise for LLM manager to handle with circuit breaker
        except APIConnectionError as e:
            logger.warning(f"Claude API connection error: {e}")
            logger.info("Falling back to alternative provider")
            raise  # Re-raise for LLM manager to handle
        except APIError as e:
            logger.warning(f"Claude API error: {e}")
            logger.info("Falling back to alternative provider")
            raise  # Re-raise for LLM manager to handle
        except Exception as e:
            logger.error(f"Unexpected error generating reply with Claude: {e}")
            raise  # Re-raise for LLM manager to handle

    def _create_prompt(self, email_data: dict, style: str) -> str:
        """
        Create a prompt for Claude to generate an email reply.

        Args:
            email_data: Email information
            style: Reply style

        Returns:
            Prompt string
        """
        subject = email_data.get('subject', 'No Subject')
        sender = email_data.get('sender', 'Unknown')
        body = email_data.get('body', '')

        style_instructions = {
            'professional': 'Write a professional, concise reply acknowledging receipt and providing brief next steps if applicable.',
            'friendly': 'Write a warm, friendly reply acknowledging receipt and offering to help.',
            'brief': 'Write a very brief, one-sentence acknowledgment.',
            'detailed': 'Write a detailed reply that thoroughly addresses the email content.'
        }

        instruction = style_instructions.get(style, style_instructions['professional'])

        prompt = f"""Generate an email reply to the following message. {instruction}

Original Email:
From: {sender}
Subject: {subject}

Content:
{body}

Guidelines:
- Generate only the reply body (no Subject: or To: lines)
- Keep it concise (2-4 sentences for professional style)
- Do not include signatures or closing remarks (will be added automatically)
- Do not make commitments you're unsure about
- Be genuine and helpful

Reply:"""

        return prompt

    def _get_intelligent_fallback_reply(self, email_data: dict) -> str:
        """
        Get intelligent fallback reply based on email content (NO API CALLS).
        Uses smart templates based on email keywords.

        Args:
            email_data: Email information

        Returns:
            Intelligent fallback reply text
        """
        subject = email_data.get('subject', '').lower()
        body = email_data.get('body', '').lower()
        sender = email_data.get('sender', '').split('<')[0].strip()

        # Extract key questions/topics
        content = f"{subject} {body}"

        # Question-based replies
        if '?' in subject or '?' in body:
            if any(word in content for word in ['how', 'what', 'when', 'where', 'why']):
                return f"""Thank you for your question. I appreciate you reaching out and I'll look into this and get back to you with details soon.

Best regards"""

        # Meeting/meeting request
        if any(word in content for word in ['meet', 'meeting', 'call', 'schedule', 'appointment']):
            return f"""Thank you for the meeting invitation. I'll check my calendar and get back to you with my availability.

Best regards"""

        # Project/work related
        if any(word in content for word in ['project', 'task', 'work', 'deadline', 'progress']):
            return f"""Thank you for the update. I've noted this and will review the details. I'll follow up with any questions or feedback.

Best regards"""

        # Feedback/appreciation
        if any(word in content for word in ['feedback', 'thank', 'appreciate', 'great', 'excellent']):
            return f"""Thank you so much for your kind words. I really appreciate your feedback.

Best regards"""

        # Information/announcement
        if any(word in content for word in ['announce', 'inform', 'notice', 'update', 'reminder']):
            return f"""Thank you for sharing this information. I've taken note of it.

Best regards"""

        # Request/help
        if any(word in content for word in ['help', 'support', 'need', 'request', 'please']):
            return f"""Thank you for reaching out. I'll be happy to assist you with this. I'll look into it and get back to you soon.

Best regards"""

        # Default intelligent reply
        return f"""Thank you for your email. I've received your message and will review it carefully. I'll get back to you soon with a response.

Best regards"""

    def _get_fallback_reply(self, email_data: dict) -> str:
        """Deprecated - use _get_intelligent_fallback_reply instead."""
        return self._get_intelligent_fallback_reply(email_data)

    def generate_summary(self, email_body: str) -> str:
        """
        Generate a summary of an email for quick review.

        Args:
            email_body: Email body text

        Returns:
            Summary text
        """
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=200,
                temperature=0.3,
                messages=[
                    {
                        "role": "user",
                        "content": f"""Provide a one-sentence summary of this email:

{email_body}

Summary:"""
                    }
                ]
            )

            summary = message.content[0].text.strip()
            logger.debug(f"Generated email summary")
            return summary

        except Exception as e:
            logger.warning(f"Error generating summary: {e}")
            return "Unable to generate summary"

    def categorize_email(self, email_data: dict) -> str:
        """
        Categorize an email for priority handling.

        Args:
            email_data: Email information

        Returns:
            Category (urgent, normal, informational, spam)
        """
        try:
            subject = email_data.get('subject', '')
            body = email_data.get('body', '')
            content = f"Subject: {subject}\n\n{body[:500]}"

            message = self.client.messages.create(
                model=self.model,
                max_tokens=10,
                temperature=0.2,
                messages=[
                    {
                        "role": "user",
                        "content": f"""Categorize this email as one of: URGENT, NORMAL, INFORMATIONAL, or SPAM.
Respond with only the category name.

{content}

Category:"""
                    }
                ]
            )

            category = message.content[0].text.strip().upper()
            valid_categories = ['URGENT', 'NORMAL', 'INFORMATIONAL', 'SPAM']
            category = category if category in valid_categories else 'NORMAL'
            logger.debug(f"Categorized email as {category}")
            return category

        except Exception as e:
            logger.warning(f"Error categorizing email: {e}")
            return 'NORMAL'
