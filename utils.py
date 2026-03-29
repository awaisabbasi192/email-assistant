"""Utility functions for email assistant."""

import re
import json
import csv
import logging
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class EmailValidator:
    """Email validation utilities."""

    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    PHONE_PATTERN = re.compile(r'^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$')

    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Check if email is valid."""
        if not email or not isinstance(email, str):
            return False
        return bool(EmailValidator.EMAIL_PATTERN.match(email.strip()))

    @staticmethod
    def is_valid_phone(phone: str) -> bool:
        """Check if phone is valid."""
        if not phone:
            return False
        return bool(EmailValidator.PHONE_PATTERN.match(phone.strip()))

    @staticmethod
    def sanitize_email(email: str) -> str:
        """Sanitize email address."""
        return email.strip().lower() if email else ""


class DataExporter:
    """Export data in various formats."""

    @staticmethod
    def export_to_csv(data: List[Dict], filepath: str, fieldnames: Optional[List[str]] = None) -> bool:
        """
        Export data to CSV.

        Args:
            data: List of dictionaries
            filepath: Output file path
            fieldnames: CSV column names (auto-detected if None)

        Returns:
            True if successful
        """
        try:
            if not data:
                logger.warning("No data to export")
                return False

            # Auto-detect fieldnames from first row
            if not fieldnames:
                fieldnames = list(data[0].keys())

            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)

            logger.info(f"Exported {len(data)} records to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            return False

    @staticmethod
    def export_to_json(data: List[Dict], filepath: str, pretty: bool = True) -> bool:
        """
        Export data to JSON.

        Args:
            data: List of dictionaries
            filepath: Output file path
            pretty: Pretty print JSON

        Returns:
            True if successful
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                if pretty:
                    json.dump(data, f, indent=2, default=str)
                else:
                    json.dump(data, f, default=str)

            logger.info(f"Exported {len(data)} records to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")
            return False

    @staticmethod
    def export_to_markdown(data: List[Dict], filepath: str, title: str = "Email Report") -> bool:
        """
        Export data to Markdown table.

        Args:
            data: List of dictionaries
            filepath: Output file path
            title: Report title

        Returns:
            True if successful
        """
        try:
            if not data:
                logger.warning("No data to export")
                return False

            fieldnames = list(data[0].keys())

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# {title}\n\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Records: {len(data)}\n\n")

                # Write table header
                f.write("| " + " | ".join(fieldnames) + " |\n")
                f.write("|" + "|".join(["---"] * len(fieldnames)) + "|\n")

                # Write table rows
                for row in data:
                    values = [str(row.get(field, "")).replace("|", "\\|") for field in fieldnames]
                    f.write("| " + " | ".join(values) + " |\n")

            logger.info(f"Exported {len(data)} records to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error exporting to Markdown: {e}")
            return False


class DataImporter:
    """Import data from various formats."""

    @staticmethod
    def import_from_csv(filepath: str) -> List[Dict]:
        """
        Import data from CSV.

        Args:
            filepath: Input file path

        Returns:
            List of dictionaries
        """
        try:
            data = []
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    data.append(row)

            logger.info(f"Imported {len(data)} records from {filepath}")
            return data
        except Exception as e:
            logger.error(f"Error importing from CSV: {e}")
            return []

    @staticmethod
    def import_from_json(filepath: str) -> List[Dict]:
        """
        Import data from JSON.

        Args:
            filepath: Input file path

        Returns:
            List of dictionaries
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if not isinstance(data, list):
                data = [data]

            logger.info(f"Imported {len(data)} records from {filepath}")
            return data
        except Exception as e:
            logger.error(f"Error importing from JSON: {e}")
            return []


class TextFormatter:
    """Text formatting utilities."""

    @staticmethod
    def truncate_text(text: str, length: int = 100, suffix: str = "...") -> str:
        """
        Truncate text to specified length.

        Args:
            text: Text to truncate
            length: Maximum length
            suffix: Suffix to add if truncated

        Returns:
            Truncated text
        """
        if not text:
            return ""
        if len(text) <= length:
            return text
        return text[:length - len(suffix)] + suffix

    @staticmethod
    def extract_email_from_string(text: str) -> Optional[str]:
        """Extract first email from text."""
        match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
        return match.group(0) if match else None

    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text."""
        if not text:
            return ""
        # Remove extra whitespace
        text = ' '.join(text.split())
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?@-]', '', text)
        return text.strip()

    @staticmethod
    def highlight_keywords(text: str, keywords: List[str]) -> str:
        """Highlight keywords in text (for markdown)."""
        if not text or not keywords:
            return text

        for keyword in keywords:
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
            text = pattern.sub(f"**{keyword}**", text)

        return text


class ReportGenerator:
    """Generate reports from email data."""

    @staticmethod
    def generate_summary_report(statistics: Dict) -> str:
        """
        Generate a summary report.

        Args:
            statistics: Statistics dictionary

        Returns:
            Report text
        """
        report = []
        report.append("=" * 60)
        report.append("EMAIL ASSISTANT - SUMMARY REPORT")
        report.append("=" * 60)
        report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        report.append("STATISTICS:")
        report.append(f"  Total Emails: {statistics.get('total_emails', 0)}")
        report.append(f"  Processed Emails: {statistics.get('processed_emails', 0)}")
        report.append(f"  Pending Drafts: {statistics.get('pending_drafts', 0)}")
        report.append(f"  Approved Drafts: {statistics.get('approved_drafts', 0)}")
        report.append(f"  Sent Drafts: {statistics.get('sent_drafts', 0)}")

        report.append("\nCATEGORY DISTRIBUTION:")
        category_dist = statistics.get('category_distribution', {})
        for category, count in sorted(category_dist.items(), key=lambda x: x[1], reverse=True):
            report.append(f"  {category.capitalize()}: {count}")

        report.append("\n" + "=" * 60 + "\n")
        return "\n".join(report)

    @staticmethod
    def save_report(content: str, filepath: str) -> bool:
        """Save report to file."""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Report saved to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving report: {e}")
            return False
