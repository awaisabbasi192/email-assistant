"""Unified LLM management with smart fallback and circuit breaker pattern."""

import logging
import time
from typing import Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Available LLM providers."""
    CLAUDE = "claude"
    OLLAMA = "ollama"
    TEMPLATE = "template"


class LLMManager:
    """
    Unified LLM management with automatic fallback and circuit breaker pattern.

    Tries Claude first, falls back to Ollama if Claude fails,
    and uses template fallback if both fail.
    """

    def __init__(self, config: dict):
        """
        Initialize LLM manager.

        Args:
            config: Configuration dictionary with 'claude' and 'ollama' settings
        """
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Initialize providers
        self.claude = None
        self.ollama = None

        # Circuit breaker state for Claude
        self.claude_failures = 0
        self.claude_circuit_open = False
        self.claude_circuit_reset_time = None
        self.max_failures_before_circuit_open = config.get('llm', {}).get('circuit_breaker_threshold', 3)
        self.circuit_breaker_reset_timeout = 300  # 5 minutes

        # Initialize available providers
        self._init_providers()

    def _init_providers(self):
        """Initialize available LLM providers."""
        # Try Claude
        try:
            from claude_integration import ClaudeReplyGenerator
            self.claude = ClaudeReplyGenerator()
            self.logger.info("Claude API initialized successfully")
        except ImportError:
            self.logger.warning("Claude integration not available (missing anthropic library)")
        except Exception as e:
            self.logger.warning(f"Claude API initialization failed: {e}")

        # Try Ollama
        try:
            from ollama_integration import OllamaReplyGenerator
            self.ollama = OllamaReplyGenerator()
            self.logger.info("Ollama integration initialized successfully")
        except Exception as e:
            self.logger.warning(f"Ollama integration initialization failed: {e}")

    def generate_reply(self, email_data: dict) -> Tuple[str, LLMProvider]:
        """
        Generate reply with automatic fallback to next provider.

        Args:
            email_data: Email data dictionary with 'subject' and 'body'

        Returns:
            Tuple of (reply_text, provider_used)
        """
        # Check if Claude circuit breaker should be reset
        if self.claude_circuit_open and self.claude_circuit_reset_time:
            if time.time() - self.claude_circuit_reset_time > self.circuit_breaker_reset_timeout:
                self.logger.info("Resetting Claude circuit breaker")
                self.claude_circuit_open = False
                self.claude_failures = 0
                self.claude_circuit_reset_time = None

        # Try Claude first (if circuit not open)
        if self.claude and not self.claude_circuit_open:
            try:
                reply = self.claude.generate_reply(email_data)
                if reply:
                    # Reset failure count on success
                    self.claude_failures = 0
                    self.logger.debug("Claude reply generated successfully")
                    return reply, LLMProvider.CLAUDE
            except Exception as e:
                self.claude_failures += 1
                self.logger.warning(f"Claude failed ({self.claude_failures}/{self.max_failures_before_circuit_open}): {e}")

                # Open circuit breaker if threshold reached
                if self.claude_failures >= self.max_failures_before_circuit_open:
                    self.claude_circuit_open = True
                    self.claude_circuit_reset_time = time.time()
                    self.logger.error("Claude circuit breaker OPEN - switching to Ollama")

        # Fallback to Ollama
        if self.ollama:
            try:
                reply = self.ollama.generate_reply(email_data)
                if reply:
                    self.logger.debug("Ollama reply generated successfully")
                    return reply, LLMProvider.OLLAMA
            except Exception as e:
                self.logger.error(f"Ollama also failed: {e}")

        # Final fallback to template
        self.logger.warning("All LLMs failed - using intelligent template fallback")
        return self._intelligent_fallback(email_data), LLMProvider.TEMPLATE

    def _intelligent_fallback(self, email_data: dict) -> str:
        """
        Generate intelligent template-based fallback reply.

        Args:
            email_data: Email data dictionary

        Returns:
            Fallback reply text
        """
        subject = (email_data.get('subject', '') or '').lower()
        body = (email_data.get('body', '') or '').lower()

        # Detect urgency
        urgent_keywords = ['urgent', 'asap', 'critical', 'emergency', 'immediately']
        is_urgent = any(keyword in subject or keyword in body for keyword in urgent_keywords)

        # Detect question
        has_question = '?' in body

        # Detect issue/problem
        problem_keywords = ['issue', 'problem', 'error', 'bug', 'broken', 'not working', 'failed']
        has_problem = any(keyword in subject or keyword in body for keyword in problem_keywords)

        # Detect request
        request_keywords = ['please', 'can you', 'could you', 'would you', 'thank you']
        has_request = any(keyword in body for keyword in request_keywords)

        # Generate appropriate response
        if is_urgent:
            return "Thank you for reaching out. I see this is urgent and have prioritized it. I'll get back to you as soon as possible with a solution."
        elif has_problem:
            return "I appreciate you reporting this. I'm looking into the issue and will provide updates shortly."
        elif has_question:
            return "Thank you for your question. I'll gather the necessary information and provide you with a comprehensive answer soon."
        elif has_request:
            return "Thank you for your request. I'll take care of this and follow up with you shortly."
        else:
            return "Thank you for your email. I've received your message and will respond shortly with more information."

    def get_provider_status(self) -> dict:
        """
        Get current status of all providers.

        Returns:
            Dictionary with provider statuses
        """
        return {
            'claude': {
                'available': self.claude is not None,
                'circuit_open': self.claude_circuit_open,
                'failure_count': self.claude_failures
            },
            'ollama': {
                'available': self.ollama is not None
            }
        }
