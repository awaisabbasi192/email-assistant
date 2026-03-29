"""Email classification and intelligent filtering."""

import logging
import json
import re
from typing import Dict, List, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class EmailClassifier:
    """Classifies emails into categories and scores priority."""

    # Common spam indicators
    SPAM_PATTERNS = {
        'promotional': r'(promo|discount|sale|offer|limited time|buy now|click here)',
        'marketing': r'(marketing|campaign|newsletter|subscribe|unsubscribe)',
        'automated': r'(automated|do not reply|no-reply|auto-response|auto-reply)',
        'financial': r'(invoice|receipt|payment|transaction|billing|balance)',
        'notification': r'(notification|alert|warning|error|confirmation)',
    }

    # Category keywords
    CATEGORY_KEYWORDS = {
        'work': [
            'project', 'deadline', 'meeting', 'schedule', 'task', 'assignment',
            'report', 'proposal', 'presentation', 'review', 'feedback', 'approval'
        ],
        'personal': [
            'hi', 'hey', 'thanks', 'help me', 'could you', 'can you', 'please',
            'friend', 'family', 'personal', 'private'
        ],
        'support': [
            'help', 'support', 'issue', 'problem', 'error', 'bug', 'fix',
            'troubleshoot', 'customer service', 'technical support'
        ],
        'marketing': [
            'promo', 'discount', 'sale', 'offer', 'coupon', 'deal',
            'limited', 'special', 'newsletter', 'subscribe'
        ],
        'bills': [
            'invoice', 'receipt', 'payment', 'billing', 'balance', 'statement',
            'charge', 'subscription', 'renew'
        ],
        'social': [
            'instagram', 'facebook', 'twitter', 'linkedin', 'youtube', 'tiktok',
            'comment', 'like', 'follow', 'friend request', 'posted'
        ],
        'newsletter': [
            'newsletter', 'digest', 'weekly', 'monthly', 'subscribe', 'unsubscribe'
        ],
    }

    # Domain reputation scores
    DOMAIN_REPUTATION = {
        'trusted_domains': [
            'google.com', 'microsoft.com', 'apple.com', 'amazon.com',
            'github.com', 'stackoverflow.com', 'gmail.com'
        ],
        'spam_domains': [
            'mailinator.com', '10minutemail.com', 'tempmail.com'
        ],
        'marketing_domains': [
            'mailchimp.com', 'sendgrid.com', 'constant contact'
        ]
    }

    def __init__(self):
        """Initialize email classifier."""
        self.category_keywords = self.CATEGORY_KEYWORDS.copy()
        self.spam_patterns = self.SPAM_PATTERNS.copy()

    def classify_email(self, email_data: Dict) -> Tuple[str, float]:
        """
        Classify email into category.

        Args:
            email_data: Email data dictionary with 'subject', 'sender', 'body'

        Returns:
            Tuple of (category, confidence_score)
        """
        subject = (email_data.get('subject', '') or '').lower()
        sender = (email_data.get('sender', '') or '').lower()
        body = (email_data.get('body', '') or '').lower()

        combined_text = f"{subject} {sender} {body}"

        # Check for urgent indicators
        if self._is_urgent(subject, body):
            return ('urgent', 0.95)

        # Check for spam
        spam_score = self._calculate_spam_score(combined_text, sender)
        if spam_score > 0.7:
            return ('spam', spam_score)

        # Classify into main categories
        category_scores: Dict[str, float] = {}

        for category, keywords in self.category_keywords.items():
            score = self._calculate_category_score(combined_text, keywords)
            if score > 0:
                category_scores[category] = score

        # Return category with highest score
        if category_scores:
            best_category = max(category_scores.items(), key=lambda x: x[1])
            return (best_category[0], min(best_category[1], 0.95))

        return ('uncategorized', 0.5)

    def score_priority(self, email_data: Dict) -> str:
        """
        Score email priority (low, normal, high, urgent).

        Args:
            email_data: Email data dictionary

        Returns:
            Priority level
        """
        subject = (email_data.get('subject', '') or '').lower()
        sender = (email_data.get('sender', '') or '').lower()

        # Urgent indicators
        urgent_patterns = [
            r'urgent', r'asap', r'immediately', r'critical',
            r'emergency', r'important', r'important: ', r'\[urgent\]',
            r're: re: ', r'fwd: fwd: '  # Multiple forwards/replies suggest importance
        ]

        for pattern in urgent_patterns:
            if re.search(pattern, subject):
                return 'urgent'

        # High priority indicators
        high_priority_patterns = [
            r'question', r'help', r'please respond', r'feedback needed',
            r'review needed', r'approval needed'
        ]

        for pattern in high_priority_patterns:
            if re.search(pattern, subject):
                return 'high'

        # Low priority indicators
        if self._is_marketing(subject) or self._is_notification(subject):
            return 'low'

        return 'normal'

    def get_spam_score(self, email_data: Dict) -> float:
        """
        Calculate spam likelihood (0.0 to 1.0).

        Args:
            email_data: Email data dictionary

        Returns:
            Spam score
        """
        subject = (email_data.get('subject', '') or '').lower()
        sender = (email_data.get('sender', '') or '').lower()
        body = (email_data.get('body', '') or '').lower()

        combined_text = f"{subject} {sender} {body}"
        return self._calculate_spam_score(combined_text, sender)

    def _calculate_spam_score(self, text: str, sender: str) -> float:
        """Calculate spam score for text."""
        score = 0.0
        matches = 0

        for category, pattern in self.spam_patterns.items():
            if re.search(pattern, text):
                matches += 1
                if category == 'automated':
                    score += 0.3
                elif category == 'promotional':
                    score += 0.2
                else:
                    score += 0.1

        # Domain reputation check
        domain = sender.split('@')[-1].strip('>')
        for spam_domain in self.DOMAIN_REPUTATION['spam_domains']:
            if spam_domain in domain:
                score += 0.4

        for marketing_domain in self.DOMAIN_REPUTATION['marketing_domains']:
            if marketing_domain in domain:
                score += 0.15

        return min(score, 1.0)

    def _calculate_category_score(self, text: str, keywords: List[str]) -> float:
        """Calculate category score based on keyword matches."""
        matches = 0
        for keyword in keywords:
            if keyword in text:
                matches += 1

        if matches == 0:
            return 0.0

        # Confidence based on match ratio
        confidence = min(matches / len(keywords), 1.0) * 0.9
        return confidence + 0.1  # Base score of 0.1

    def _is_urgent(self, subject: str, body: str) -> bool:
        """Check if email is urgent."""
        urgent_patterns = [
            r'\[urgent\]', r'urgent', r'asap', r'immediately',
            r'critical', r'emergency'
        ]

        for pattern in urgent_patterns:
            if re.search(pattern, subject):
                return True

        return False

    def _is_marketing(self, subject: str) -> bool:
        """Check if email is marketing."""
        marketing_patterns = [
            r'promo', r'discount', r'sale', r'offer', r'coupon',
            r'limited time', r'special offer', r'unsubscribe'
        ]

        for pattern in marketing_patterns:
            if re.search(pattern, subject):
                return True

        return False

    def _is_notification(self, subject: str) -> bool:
        """Check if email is notification."""
        notification_patterns = [
            r'notification', r'alert', r'reminder', r'confirmation',
            r'receipt', r'receipt', r'password reset'
        ]

        for pattern in notification_patterns:
            if re.search(pattern, subject):
                return True

        return False

    def extract_sender_name(self, sender: str) -> str:
        """
        Extract readable sender name from email address.

        Args:
            sender: Full sender email (e.g., "John Doe <john@example.com>")

        Returns:
            Sender name or email address
        """
        if '<' in sender:
            name = sender.split('<')[0].strip('"').strip()
            return name if name else sender

        if '@' in sender:
            return sender.split('@')[0]

        return sender

    def get_all_categories(self) -> List[str]:
        """
        Get list of all available categories.

        Returns:
            List of category names
        """
        return list(self.category_keywords.keys()) + ['urgent', 'spam', 'uncategorized']

    def batch_classify(self, emails: List[Dict]) -> List[Tuple[Dict, str, float]]:
        """
        Classify multiple emails in batch.

        Args:
            emails: List of email dictionaries

        Returns:
            List of (email, category, confidence) tuples
        """
        results = []
        for email in emails:
            category, confidence = self.classify_email(email)
            results.append((email, category, confidence))
        return results

    def get_category_confidence(self, email_data: Dict) -> Dict[str, float]:
        """
        Get confidence scores for all categories.

        Args:
            email_data: Email data dictionary

        Returns:
            Dictionary mapping categories to confidence scores
        """
        subject = (email_data.get('subject', '') or '').lower()
        sender = (email_data.get('sender', '') or '').lower()
        body = (email_data.get('body', '') or '').lower()
        combined_text = f"{subject} {sender} {body}"

        scores = {}

        # Check special categories first
        if self._is_urgent(subject, body):
            scores['urgent'] = 0.95
        else:
            spam_score = self.get_spam_score(email_data)
            if spam_score > 0.7:
                scores['spam'] = spam_score
            else:
                # Calculate scores for all categories
                for category, keywords in self.category_keywords.items():
                    score = self._calculate_category_score(combined_text, keywords)
                    if score > 0:
                        scores[category] = score

        return scores
