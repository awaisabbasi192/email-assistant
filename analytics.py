"""Email analytics and reporting."""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from database import DatabaseManager

logger = logging.getLogger(__name__)


class EmailAnalytics:
    """Analyzes email patterns and generates statistics."""

    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize analytics engine.

        Args:
            db_manager: DatabaseManager instance
        """
        self.db = db_manager

    def generate_daily_analytics(self, date: Optional[str] = None) -> Dict:
        """
        Generate analytics for a specific date.

        Args:
            date: Date in YYYY-MM-DD format (default: today)

        Returns:
            Analytics dictionary
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        # Get email stats
        all_emails = self.db.get_all_emails(limit=10000)
        emails_today = [e for e in all_emails if e['created_at'].startswith(date)]

        # Count processed emails
        processed_today = [e for e in emails_today if e['is_processed']]

        # Category distribution
        category_dist = self._calculate_category_distribution(emails_today)

        # Calculate metrics
        total_emails = len(emails_today)
        processed_count = len(processed_today)
        avg_response_time = self._calculate_avg_response_time(processed_today) if processed_today else 0

        # Store analytics
        self.db.add_analytics(
            date=date,
            total_emails=total_emails,
            processed_emails=processed_count,
            category_distribution=category_dist
        )

        return {
            'date': date,
            'total_emails': total_emails,
            'processed_emails': processed_count,
            'processing_rate': (processed_count / total_emails * 100) if total_emails > 0 else 0,
            'category_distribution': category_dist,
            'avg_response_time': avg_response_time
        }

    def get_weekly_analytics(self, weeks: int = 1) -> Dict:
        """
        Get analytics for past N weeks.

        Args:
            weeks: Number of weeks to analyze

        Returns:
            Weekly analytics summary
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=weeks * 7)

        analytics_range = self.db.get_analytics_range(
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )

        total_emails = sum(a['total_emails'] for a in analytics_range)
        total_processed = sum(a['processed_emails'] for a in analytics_range)

        return {
            'period': f'Last {weeks} week(s)',
            'total_emails': total_emails,
            'processed_emails': total_processed,
            'processing_rate': (total_processed / total_emails * 100) if total_emails > 0 else 0,
            'daily_data': analytics_range
        }

    def get_monthly_analytics(self) -> Dict:
        """Get analytics for current month."""
        today = datetime.now()
        first_of_month = today.replace(day=1)

        analytics_range = self.db.get_analytics_range(
            first_of_month.strftime('%Y-%m-%d'),
            today.strftime('%Y-%m-%d')
        )

        total_emails = sum(a['total_emails'] for a in analytics_range)
        total_processed = sum(a['processed_emails'] for a in analytics_range)

        return {
            'period': f'{today.strftime("%B %Y")}',
            'total_emails': total_emails,
            'processed_emails': total_processed,
            'processing_rate': (total_processed / total_emails * 100) if total_emails > 0 else 0,
            'daily_data': analytics_range
        }

    def get_sender_frequency(self, limit: int = 10) -> List[Dict]:
        """
        Get most frequent senders.

        Args:
            limit: Number of top senders to return

        Returns:
            List of sender statistics
        """
        all_emails = self.db.get_all_emails(limit=10000)

        sender_counts: Dict[str, int] = {}
        for email in all_emails:
            sender = email['sender']
            sender_counts[sender] = sender_counts.get(sender, 0) + 1

        # Sort by count
        sorted_senders = sorted(sender_counts.items(), key=lambda x: x[1], reverse=True)

        return [
            {'sender': sender, 'count': count}
            for sender, count in sorted_senders[:limit]
        ]

    def get_email_by_hour(self) -> Dict[int, int]:
        """
        Get email distribution by hour of day.

        Returns:
            Dictionary mapping hour (0-23) to email count
        """
        all_emails = self.db.get_all_emails(limit=10000)

        hour_distribution: Dict[int, int] = {i: 0 for i in range(24)}

        for email in all_emails:
            try:
                timestamp = email['created_at']
                if timestamp:
                    hour = int(timestamp.split('T')[1].split(':')[0])
                    hour_distribution[hour] += 1
            except (IndexError, ValueError):
                pass

        return hour_distribution

    def get_email_by_day_of_week(self) -> Dict[str, int]:
        """
        Get email distribution by day of week.

        Returns:
            Dictionary mapping day name to email count
        """
        all_emails = self.db.get_all_emails(limit=10000)

        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_distribution = {day: 0 for day in days}

        for email in all_emails:
            try:
                timestamp = email['created_at']
                if timestamp:
                    date_obj = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    day_name = days[date_obj.weekday()]
                    day_distribution[day_name] += 1
            except (ValueError, IndexError):
                pass

        return day_distribution

    def get_processing_rate_trend(self, days: int = 30) -> List[Dict]:
        """
        Get processing rate trend over N days.

        Args:
            days: Number of days to analyze

        Returns:
            List of daily processing rates
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        analytics_range = self.db.get_analytics_range(
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )

        trend = []
        for analytics in analytics_range:
            rate = (
                (analytics['processed_emails'] / analytics['total_emails'] * 100)
                if analytics['total_emails'] > 0
                else 0
            )
            trend.append({
                'date': analytics['date'],
                'processing_rate': rate,
                'total_emails': analytics['total_emails'],
                'processed_emails': analytics['processed_emails']
            })

        return trend

    def export_analytics_csv(self, start_date: str, end_date: str) -> str:
        """
        Export analytics to CSV format.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            CSV formatted string
        """
        analytics_range = self.db.get_analytics_range(start_date, end_date)

        csv_lines = ['Date,Total Emails,Processed Emails,Processing Rate (%)']

        for analytics in analytics_range:
            rate = (
                (analytics['processed_emails'] / analytics['total_emails'] * 100)
                if analytics['total_emails'] > 0
                else 0
            )
            csv_lines.append(
                f"{analytics['date']},{analytics['total_emails']},{analytics['processed_emails']},{rate:.2f}"
            )

        return '\n'.join(csv_lines)

    def _calculate_category_distribution(self, emails: List) -> Dict[str, int]:
        """Calculate distribution of emails by category."""
        distribution: Dict[str, int] = {}

        for email in emails:
            category = email.get('category', 'uncategorized')
            distribution[category] = distribution.get(category, 0) + 1

        return distribution

    def _calculate_avg_response_time(self, emails: List) -> float:
        """
        Calculate average response time in hours.

        Args:
            emails: List of processed emails

        Returns:
            Average response time in hours
        """
        if not emails:
            return 0.0

        total_hours = 0
        for email in emails:
            try:
                created = datetime.fromisoformat(email['created_at'].replace('Z', '+00:00'))
                updated = datetime.fromisoformat(email['updated_at'].replace('Z', '+00:00'))
                hours = (updated - created).total_seconds() / 3600
                total_hours += hours
            except (ValueError, TypeError, KeyError):
                pass

        return total_hours / len(emails) if emails else 0.0

    def get_summary_statistics(self) -> Dict:
        """Get overall summary statistics."""
        all_emails = self.db.get_all_emails(limit=10000)
        total_count = self.db.get_email_count()
        processed_count = self.db.get_processed_count()
        pending_drafts = self.db.get_draft_count('pending')

        return {
            'total_emails': total_count,
            'processed_emails': processed_count,
            'pending_drafts': pending_drafts,
            'processing_rate': (processed_count / total_count * 100) if total_count > 0 else 0,
            'category_distribution': self.db.get_category_distribution(),
            'sender_frequency': self.get_sender_frequency(5),
            'email_by_hour': self.get_email_by_hour(),
            'email_by_day': self.get_email_by_day_of_week()
        }
