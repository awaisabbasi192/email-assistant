"""Ollama local LLM integration for email reply generation."""

import logging
import requests
import json
import re
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry as UrllibRetry

logger = logging.getLogger(__name__)

OLLAMA_BASE_URL = "http://127.0.0.1:11434"
OLLAMA_MODEL = "mistral"


class OllamaReplyGenerator:
    """Generates email replies using local Ollama LLM (FREE & OFFLINE)."""

    def __init__(self, model: str = OLLAMA_MODEL, timeout: int = 60, max_retries: int = 3):
        """
        Initialize Ollama reply generator.

        Args:
            model: Ollama model to use (mistral, llama2, neural-chat, etc.)
            timeout: Initial timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.model = model
        self.base_url = OLLAMA_BASE_URL
        self.timeout = timeout
        self.max_retries = max_retries

        # Initialize persistent session with connection pooling
        self.session = self._create_session()

        self._check_ollama_connection()

    def _create_session(self):
        """Create requests session with connection pooling and retry strategy."""
        session = requests.Session()

        # Configure retry strategy
        retry_strategy = UrllibRetry(
            total=self.max_retries,
            backoff_factor=1,  # Exponential backoff: 1s, 2s, 4s, 8s
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST", "OPTIONS"]
        )

        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=20
        )

        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def _check_ollama_connection(self):
        """Check if Ollama service is running."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                logger.info(f"Connected to Ollama server at {self.base_url}")
                models = response.json().get('models', [])
                model_names = [m.get('name', '').split(':')[0] for m in models]
                logger.info(f"Available models: {model_names}")

                if not any(self.model in name for name in model_names):
                    logger.warning(f"Model '{self.model}' not found. Please run: ollama pull {self.model}")
            else:
                raise Exception("Ollama server not responding")
        except Exception as e:
            logger.error(f"Ollama connection failed: {e}")
            logger.error("Make sure Ollama is running. Execute: ollama serve")
            raise

    def generate_reply(self, email_data: dict) -> str:
        """
        Generate an email reply using local Ollama model with retry logic.

        Args:
            email_data: Dictionary containing 'subject', 'sender', 'body'

        Returns:
            Generated reply text
        """
        prompt = self._create_prompt(email_data)
        logger.debug(f"Sending request to Ollama model: {self.model}")

        # Try with exponential backoff
        for attempt in range(self.max_retries):
            try:
                # Adaptive timeout: increase on retries
                timeout = self.timeout * (2 ** attempt) if attempt > 0 else self.timeout
                logger.debug(f"Ollama request attempt {attempt + 1}/{self.max_retries} (timeout: {timeout}s)")

                response = self.session.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "temperature": 0.7,
                        "num_predict": 150,
                    },
                    timeout=timeout
                )

                if response.status_code == 200:
                    result = response.json()
                    reply = result.get('response', '').strip()

                    if reply:
                        email_type = self._analyze_email_type(email_data)
                        logger.info(f"✓ Generated {email_type} reply using Ollama")
                        return reply
                    else:
                        logger.warning("Empty response from Ollama, trying fallback")
                        return self._get_fallback_reply(email_data)
                else:
                    logger.error(f"Ollama error (status {response.status_code}), retrying...")
                    if attempt < self.max_retries - 1:
                        wait_time = 2 ** attempt
                        logger.info(f"Waiting {wait_time}s before retry...")
                        time.sleep(wait_time)
                    continue

            except requests.exceptions.Timeout as e:
                logger.warning(f"Ollama timeout on attempt {attempt + 1}/{self.max_retries}: {e}")
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.info(f"Waiting {wait_time}s before retry (exponential backoff)...")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error("Ollama timeout after all retries - using fallback")
                    return self._get_fallback_reply(email_data)

            except requests.exceptions.ConnectionError as e:
                logger.warning(f"Ollama connection error on attempt {attempt + 1}/{self.max_retries}: {e}")
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.info(f"Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error("Cannot connect to Ollama after all retries. Make sure 'ollama serve' is running")
                    return self._get_fallback_reply(email_data)

            except requests.exceptions.RequestException as e:
                logger.error(f"Ollama request error on attempt {attempt + 1}/{self.max_retries}: {e}")
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.info(f"Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error("Failed to get response from Ollama after all retries")
                    return self._get_fallback_reply(email_data)

        # If all retries exhausted
            logger.error("All Ollama retry attempts failed - using fallback")
            return self._get_fallback_reply(email_data)

        except KeyboardInterrupt:
            logger.info("Interrupted by user during reply generation")
            raise
        except Exception as e:
            logger.error(f"Error generating reply with Ollama: {e}")
            return self._get_fallback_reply(email_data)

    def _analyze_email_type(self, email_data: dict) -> str:
        """Analyze what type of email this is."""
        subject = email_data.get('subject', '').lower()
        body = email_data.get('body', '').lower()
        combined = f"{subject} {body}"

        # Determine email type
        if re.search(r'\?|question|ask|could you|can you|what|how|when|where|why|would you', combined):
            return "question"
        elif re.search(r'problem|issue|error|not working|bug|help|support|urgent|asap|broken', combined):
            return "problem"
        elif re.search(r'thank|thanks|appreciate|grateful|thanks for|thanks so much', combined):
            return "thanks"
        elif re.search(r'feedback|opinion|review|thoughts|what do you think|please comment', combined):
            return "feedback"
        elif re.search(r'meeting|call|schedule|time|availability|let\'s meet', combined):
            return "meeting"
        elif re.search(r'update|fyi|heads up|just to let you|just a reminder|reminder|following up', combined):
            return "update"
        elif re.search(r'request|need|require|would like|interested|looking for|need help', combined):
            return "request"
        else:
            return "general"

    def _create_prompt(self, email_data: dict) -> str:
        """Create a prompt for Ollama to generate email reply based on actual email content."""
        subject = email_data.get('subject', 'No Subject')
        sender = email_data.get('sender', 'Unknown')
        body = email_data.get('body', '')

        # Analyze email type
        email_type = self._analyze_email_type(email_data)

        # Create type-specific instructions
        type_instructions = {
            "question": "The sender is asking a specific question. Answer it directly and clearly without being too formal.",
            "problem": "The sender is reporting a problem or issue. Show empathy, acknowledge the problem, and offer to help resolve it.",
            "thanks": "The sender is thanking you for something. Acknowledge their thanks warmly and naturally, without being overly formal.",
            "feedback": "The sender is providing feedback or asking for your opinion. Acknowledge it and show you value their input.",
            "meeting": "The sender is trying to schedule a meeting or call. Acknowledge their request and offer flexibility with timing.",
            "update": "The sender is sharing an update or reminder. Acknowledge it briefly and naturally.",
            "request": "The sender is requesting something from you. Show you understand their need and indicate you'll handle it.",
            "general": "Write a natural reply that addresses what they said."
        }

        prompt = f"""You are a professional email assistant. Read this email carefully and write a specific, personalized reply that sounds natural and human.

EMAIL TYPE: This is a {email_type} email.
CONTEXT: {type_instructions.get(email_type, type_instructions["general"])}

ORIGINAL EMAIL:
From: {sender}
Subject: {subject}
Body: {body}

---

RULES FOR YOUR REPLY:
1. Address the SPECIFIC content of THIS email - not a generic response
2. Keep it natural and conversational (2-4 sentences max)
3. Match their tone - casual if they're casual, professional if they're professional
4. NEVER start with "Thank you for reaching out" or similar generic phrases
5. NEVER use formal closings like "Best regards" or "Sincerely"
6. Show you actually read and understood their email
7. Be concise and helpful

Now write ONLY the reply body (no greeting, no subject line, no signature):"""

        return prompt

    def _get_fallback_reply(self, email_data: dict) -> str:
        """Fallback reply if Ollama fails - contextual based on email content."""
        subject = email_data.get('subject', '').lower()
        body = email_data.get('body', '').lower()
        sender_name = email_data.get('sender', '').split('@')[0].split('<')[0].strip()

        # Analyze email body for context
        is_question = '?' in body or 'please' in body or 'can you' in body or 'could you' in body
        is_urgent = 'urgent' in subject or 'asap' in subject or 'urgent' in body or 'emergency' in body
        is_follow_up = 'follow' in subject or 'follow up' in body or 'reminder' in subject
        is_feedback = 'feedback' in subject or 'review' in subject or 'opinion' in subject
        is_problem = 'issue' in subject or 'problem' in subject or 'error' in subject or 'not working' in body
        is_thanks = 'thank' in subject or 'thanks' in subject or 'appreciate' in subject or 'thanks' in body
        is_meeting = 'meeting' in subject or 'call' in subject or 'schedule' in subject or 'time' in subject

        # Generate contextual fallback
        if is_thanks:
            return f"Thanks so much! I appreciate that. Let me look into this and get back to you."
        elif is_urgent:
            return f"Got it - I see this is urgent. I'm on it and will update you shortly."
        elif is_problem:
            return f"Sorry to hear you're having trouble. Let me investigate this and find a solution for you."
        elif is_follow_up:
            return f"Yes, still on my radar. I'll have an update for you very soon."
        elif is_question:
            return f"Good question. Let me look into that and get you an answer."
        elif is_meeting:
            return f"Thanks for reaching out. Let me check my availability and find a good time."
        elif is_feedback:
            return f"Thanks for the feedback, that's really helpful. I'll take this into account."
        else:
            return f"Thanks for reaching out. I'll look into this and get back to you soon."


class OllamaClassifier:
    """Uses Ollama to classify emails into categories."""

    def __init__(self, model: str = "mistral"):
        """
        Initialize Ollama classifier.

        Args:
            model: Ollama model to use for classification
        """
        self.model = model
        self.base_url = OLLAMA_BASE_URL
        self._check_ollama_connection()

    def _check_ollama_connection(self):
        """Check if Ollama service is running."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                logger.info(f"Connected to Ollama for classification")
            else:
                raise Exception("Ollama server not responding")
        except Exception as e:
            logger.error(f"Ollama connection failed for classifier: {e}")
            raise

    def classify_email(self, email_data: dict) -> tuple:
        """
        Classify email using Ollama.

        Args:
            email_data: Dictionary with 'subject', 'sender', 'body'

        Returns:
            Tuple of (category, confidence_score)
        """
        try:
            prompt = self._create_classification_prompt(email_data)

            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.3,  # Lower temp for consistent classification
                    "num_predict": 50,
                },
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                category_text = result.get('response', '').strip().lower()
                category, confidence = self._parse_classification_response(category_text)
                logger.info(f"Classified email as: {category} ({confidence:.2f})")
                return category, confidence
            else:
                logger.warning(f"Ollama classification failed: {response.status_code}")
                return "uncategorized", 0.5

        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to Ollama for classification")
            return "uncategorized", 0.5
        except Exception as e:
            logger.error(f"Error classifying email: {e}")
            return "uncategorized", 0.5

    def _create_classification_prompt(self, email_data: dict) -> str:
        """Create a prompt for email classification."""
        subject = email_data.get('subject', 'No Subject')
        sender = email_data.get('sender', 'Unknown')
        body = email_data.get('body', '')[:500]

        prompt = f"""Classify this email into ONE category from: personal, work, support, marketing, bills, social, newsletter, urgent, spam.

Email:
From: {sender}
Subject: {subject}
Content: {body}

Answer with ONLY the category name and a confidence score (0-1) in this format:
category: [category_name]
confidence: [score]
"""
        return prompt

    def _parse_classification_response(self, response: str) -> tuple:
        """Parse classification response from Ollama."""
        categories = ["personal", "work", "support", "marketing", "bills", "social", "newsletter", "urgent", "spam"]

        # Extract category
        category = "uncategorized"
        for cat in categories:
            if cat in response.lower():
                category = cat
                break

        # Extract confidence score
        confidence = 0.5
        try:
            if "confidence:" in response.lower():
                score_text = response.lower().split("confidence:")[-1].strip()
                score = float(score_text.split('\n')[0].strip())
                confidence = max(0.0, min(1.0, score))
        except (ValueError, IndexError):
            pass

        return category, confidence
