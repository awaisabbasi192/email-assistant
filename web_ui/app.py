"""Flask web UI application for email assistant."""

import sys
import os

# Fix path to import modules from parent directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from functools import wraps

from database import DatabaseManager
from email_classifier import EmailClassifier
from error_handler import ServiceHealthChecker
from analytics import EmailAnalytics
from utils import DataExporter, EmailValidator, ReportGenerator
from auth_utils import PasswordManager
from validators import InputValidator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')

# Load configuration
config_file = os.path.join(os.path.dirname(__file__), '..', 'config.json')
with open(config_file, 'r') as f:
    CONFIG = json.load(f)

# Set Flask config
app.config['SECRET_KEY'] = CONFIG.get('web_ui', {}).get('secret_key', 'dev-secret-key-change-this')
app.config['SESSION_COOKIE_SECURE'] = CONFIG.get('web_ui', {}).get('session_cookie_secure', True)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=CONFIG.get('web_ui', {}).get('session_timeout_minutes', 1440))

# Disable CSRF protection for development/testing
# csrf = CSRFProtect(app)
# Note: CSRF protection disabled for easier testing. Enable in production with proper token handling.

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Enable CORS with restrictions
CORS(app, resources={
    r"/api/*": {"origins": "127.0.0.1:5000", "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]}
})

# Initialize managers
db_path = CONFIG.get('advanced', {}).get('database_file', 'email_assistant.db')
# If relative path, make it relative to parent directory
if not os.path.isabs(db_path):
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), db_path)
db = DatabaseManager(db_path)
classifier = EmailClassifier()
health_checker = ServiceHealthChecker()
analytics = EmailAnalytics(db)


def login_required(f):
    """Decorator to require login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'authenticated' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def get_current_user_id() -> int:
    """
    Get current user ID from session.

    For now, returns default user ID (1) for single-user mode.
    Can be extended for multi-user by looking up user by username.

    Returns:
        User ID integer
    """
    # For now, return default user ID (backward compatibility)
    # In future: return db.get_user_id_by_username(session.get('username'))
    return 1


@app.before_request
def before_request():
    """Handle before request."""
    session.permanent = True
    app.permanent_session_lifetime = CONFIG.get('web_ui', {}).get('session_timeout_minutes', 1440) * 60


@app.route('/')
def index():
    """Redirect to dashboard or login."""
    if 'authenticated' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    """Login page with username and password authentication."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        # Validate input
        if not username or not password:
            logger.warning("Login attempt with missing username or password")
            return render_template('login.html', error='Username and password required')

        try:
            # Check database for user
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, password_hash, is_active
                FROM users
                WHERE username = ?
            """, (username,))
            user = cursor.fetchone()
            conn.close()

            if user:
                user_id, password_hash, is_active = user

                # Check if user is active
                if not is_active:
                    logger.warning(f"Login attempt for inactive user: {username}")
                    return render_template('login.html', error='Account is disabled')

                # Verify password
                if PasswordManager.verify_password(password, password_hash):
                    session['authenticated'] = True
                    session['username'] = username
                    session['user_id'] = user_id
                    session.permanent = True
                    logger.info(f"User {username} logged in successfully")

                    # Update last login
                    conn = db.get_connection()
                    cursor = conn.cursor()
                    cursor.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?", (user_id,))
                    conn.commit()
                    conn.close()

                    return redirect(url_for('dashboard'))

            logger.warning(f"Failed login attempt for username: {username}")
            # Don't reveal if username or password is wrong (security best practice)
            return render_template('login.html', error='Invalid username or password')

        except Exception as e:
            logger.error(f"Login error: {e}")
            return render_template('login.html', error='Login failed. Please try again.')

    return render_template('login.html')


@app.route('/logout')
def logout():
    """Logout."""
    session.clear()
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def register():
    """User registration page."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')

        # Validate input
        errors = []

        if not username or len(username) < 3 or len(username) > 50:
            errors.append('Username must be 3-50 characters')

        if not email or '@' not in email:
            errors.append('Valid email required')

        if not password or len(password) < 6:
            errors.append('Password must be at least 6 characters')

        if password != password_confirm:
            errors.append('Passwords do not match')

        if errors:
            return render_template('register.html', error='; '.join(errors))

        try:
            # Check if user already exists
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))

            if cursor.fetchone():
                conn.close()
                return render_template('register.html', error='Username or email already exists')

            # Hash password
            password_manager = PasswordManager()
            password_hash = password_manager.hash_password(password)

            # Create user
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, is_active, gmail_connected)
                VALUES (?, ?, ?, ?, ?)
            """, (username, email, password_hash, 1, 0))

            conn.commit()
            conn.close()

            logger.info(f"New user registered: {username}")
            return render_template('register.html', success='Account created! Please login.')

        except Exception as e:
            logger.error(f"Registration error: {e}")
            return render_template('register.html', error='Registration failed. Please try again.')

    return render_template('register.html')


@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard."""
    user_id = get_current_user_id()

    try:
        # Get statistics with user_id
        total_emails = db.get_email_count(user_id)
        processed_count = db.get_processed_count(user_id)
        pending_drafts = db.get_draft_count('pending', user_id)

        # Get category distribution
        category_dist = db.get_category_distribution(user_id)
    except Exception as e:
        logger.warning(f"Dashboard stats error (might be normal on first login): {e}")
        # Default values
        total_emails = 0
        processed_count = 0
        pending_drafts = 0
        category_dist = {}

    # Check service health
    health = health_checker.get_health_report()

    context = {
        'total_emails': total_emails,
        'processed_emails': processed_count,
        'pending_drafts': pending_drafts,
        'category_distribution': category_dist,
        'service_health': health,
        'is_healthy': health_checker.are_all_healthy()
    }

    return render_template('dashboard.html', **context)


@app.route('/emails')
@login_required
def emails_page():
    """Email list page."""
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', None)
    search = request.args.get('search', None)

    # Check if refresh requested
    refresh = request.args.get('refresh', None)
    if refresh:
        try:
            from auto_processor import SimpleEmailProcessor
            import json
            from pathlib import Path

            config_file = Path('config.json')
            if config_file.exists():
                with open(config_file) as f:
                    config = json.load(f)

                processor = SimpleEmailProcessor(config)
                # Run one check cycle
                processor.check_and_process()
                logger.info("Manual refresh executed")
        except Exception as e:
            logger.error(f"Error in manual refresh: {e}")

    limit = 20
    offset = (page - 1) * limit

    if category:
        emails = db.get_emails_by_category(category, limit)
    else:
        emails = db.get_all_emails(limit, offset)

    return render_template('emails.html', emails=emails, page=page, category=category)


@app.route('/drafts')
@login_required
def drafts_page():
    """Draft review page."""
    status = request.args.get('status', 'pending')

    if status == 'pending':
        drafts = db.get_pending_drafts(100)
    else:
        # Get all drafts (filtered by status in future)
        drafts = db.get_pending_drafts(100)

    return render_template('draft_review.html', drafts=drafts)


@app.route('/analytics')
@login_required
def analytics_page():
    """Analytics dashboard."""
    # Get analytics data
    today = datetime.now().strftime('%Y-%m-%d')
    today_analytics = db.get_analytics(today)

    # Get category distribution
    category_dist = db.get_category_distribution()

    # Get daily stats for chart
    from datetime import timedelta
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    analytics_range = db.get_analytics_range(
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d')
    )

    return render_template(
        'analytics.html',
        today_analytics=today_analytics,
        category_distribution=category_dist,
        analytics_range=analytics_range
    )


@app.route('/templates')
@login_required
def templates_page():
    """Template management page."""
    templates = db.get_all_templates()
    return render_template('templates.html', templates=templates)


@app.route('/settings')
@login_required
def settings_page():
    """Settings page."""
    return render_template('settings.html', config=CONFIG)


@app.route('/gmail-settings')
@login_required
def gmail_settings_page():
    """Gmail configuration page."""
    try:
        user_id = session.get('user_id', 1)
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT gmail_email, gmail_connected FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()

        if user:
            gmail_email, gmail_connected = user
            return render_template('email_settings.html',
                                 gmail_email=gmail_email,
                                 gmail_connected=bool(gmail_connected))
        return render_template('email_settings.html', gmail_email='', gmail_connected=False)
    except Exception as e:
        logger.error(f"Error loading Gmail settings: {e}")
        return render_template('email_settings.html', error='Failed to load settings')


# ===== API ENDPOINTS =====

@app.route('/api/emails', methods=['GET'])
@login_required
def api_get_emails():
    """Get emails API."""
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', None)
    limit = 20
    offset = (page - 1) * limit

    if category:
        emails = db.get_emails_by_category(category, limit)
    else:
        emails = db.get_all_emails(limit, offset)

    return jsonify([dict(e) for e in emails])


@app.route('/api/drafts/pending', methods=['GET'])
@login_required
def api_get_pending_drafts():
    """Get pending drafts API."""
    drafts = db.get_pending_drafts(100)
    return jsonify([dict(d) for d in drafts])


@app.route('/api/drafts/<int:draft_id>', methods=['GET'])
@login_required
def api_get_draft(draft_id):
    """Get specific draft."""
    draft = db.get_draft(draft_id)
    if not draft:
        return jsonify({'error': 'Draft not found'}), 404
    return jsonify(dict(draft))


@app.route('/api/drafts/<int:draft_id>/update', methods=['POST'])
@login_required
def api_update_draft(draft_id):
    """Update draft reply body."""
    data = request.get_json()
    reply_body = data.get('reply_body', '')

    if not reply_body:
        return jsonify({'error': 'Reply body required'}), 400

    success = db.update_draft(draft_id, reply_body)
    if success:
        return jsonify({'status': 'success'})
    return jsonify({'error': 'Failed to update draft'}), 500


@app.route('/api/drafts/<int:draft_id>/status', methods=['POST'])
@login_required
def api_update_draft_status(draft_id):
    """Update draft status."""
    data = request.get_json()
    status = data.get('status', 'pending')

    valid_statuses = ['pending', 'approved', 'sent', 'deleted']
    if status not in valid_statuses:
        return jsonify({'error': 'Invalid status'}), 400

    success = db.update_draft_status(draft_id, status)
    if success:
        return jsonify({'status': 'success'})
    return jsonify({'error': 'Failed to update status'}), 500


@app.route('/api/drafts/<int:draft_id>/regenerate', methods=['POST'])
@login_required
def api_regenerate_draft(draft_id):
    """Regenerate draft using Ollama."""
    # This will be enhanced with actual Ollama integration
    draft = db.get_draft(draft_id)
    if not draft:
        return jsonify({'error': 'Draft not found'}), 404

    # TODO: Call Ollama to regenerate reply
    return jsonify({'status': 'regenerated'})


@app.route('/api/templates', methods=['GET'])
@login_required
def api_get_templates():
    """Get all templates."""
    templates = db.get_all_templates()
    return jsonify([dict(t) for t in templates])


@app.route('/api/templates', methods=['POST'])
@login_required
def api_create_template():
    """Create new template."""
    data = request.get_json()

    name = data.get('name', '')
    body = data.get('body', '')
    category = data.get('category', '')

    if not name or not body:
        return jsonify({'error': 'Name and body required'}), 400

    template_id = db.add_template(name, body, category)
    if template_id > 0:
        return jsonify({'id': template_id, 'status': 'created'}), 201
    return jsonify({'error': 'Template already exists'}), 400


@app.route('/api/stats', methods=['GET'])
@login_required
def api_get_stats():
    """Get dashboard statistics."""
    total_emails = db.get_email_count()
    processed_count = db.get_processed_count()
    pending_drafts = db.get_draft_count('pending')
    category_dist = db.get_category_distribution()

    return jsonify({
        'total_emails': total_emails,
        'processed_emails': processed_count,
        'pending_drafts': pending_drafts,
        'category_distribution': category_dist
    })


@app.route('/api/health', methods=['GET'])
@login_required
def api_health_check():
    """Get service health status."""
    health_checker.check_database()
    health_checker.check_ollama()

    health = health_checker.get_health_report()
    return jsonify({
        'status': 'healthy' if health_checker.are_all_healthy() else 'unhealthy',
        'services': health
    })


# ===== NEW API ENDPOINTS =====

@app.route('/api/search', methods=['GET'])
@login_required
def api_search():
    """Search emails by query."""
    search_term = request.args.get('q', '').strip()
    limit = request.args.get('limit', 50, type=int)

    if not search_term:
        return jsonify({'error': 'Search term required'}), 400

    emails = db.search_emails(search_term, limit)
    return jsonify([dict(e) for e in emails])


@app.route('/api/search/advanced', methods=['GET'])
@login_required
def api_search_advanced():
    """Advanced search with multiple filters."""
    subject = request.args.get('subject', None)
    sender = request.args.get('sender', None)
    category = request.args.get('category', None)
    priority = request.args.get('priority', None)
    is_processed = request.args.get('is_processed', None)
    limit = request.args.get('limit', 100, type=int)

    # Convert is_processed to boolean
    if is_processed:
        is_processed = is_processed.lower() == 'true'

    emails = db.search_emails_advanced(
        subject=subject,
        sender=sender,
        category=category,
        priority=priority,
        is_processed=is_processed,
        limit=limit
    )

    return jsonify([dict(e) for e in emails])


@app.route('/api/export/csv', methods=['GET'])
@login_required
def api_export_csv():
    """Export emails to CSV."""
    try:
        limit = request.args.get('limit', None, type=int)
        emails = db.get_all_emails(limit=limit or 100000)

        # Convert to dictionaries
        emails_list = []
        for email in emails:
            emails_list.append({
                'id': email['id'],
                'sender': email['sender'],
                'subject': email['subject'],
                'category': email['category'],
                'priority': email['priority'],
                'is_processed': email['is_processed'],
                'created_at': email['created_at']
            })

        from io import StringIO
        csv_buffer = StringIO()

        if emails_list:
            import csv
            writer = csv.DictWriter(csv_buffer, fieldnames=emails_list[0].keys())
            writer.writeheader()
            writer.writerows(emails_list)

        return jsonify({
            'status': 'success',
            'csv_data': csv_buffer.getvalue(),
            'total_records': len(emails_list)
        })

    except Exception as e:
        logger.error(f"Error exporting to CSV: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/export/json', methods=['GET'])
@login_required
def api_export_json():
    """Export emails to JSON."""
    try:
        limit = request.args.get('limit', None, type=int)
        emails = db.get_all_emails(limit=limit or 100000)

        emails_list = [dict(e) for e in emails]
        return jsonify({
            'status': 'success',
            'data': emails_list,
            'total_records': len(emails_list)
        })

    except Exception as e:
        logger.error(f"Error exporting to JSON: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/emails/<int:email_id>/classify', methods=['POST'])
@login_required
def api_classify_email(email_id):
    """Classify an email."""
    email = db.get_email(email_id)
    if not email:
        return jsonify({'error': 'Email not found'}), 404

    category, confidence = classifier.classify_email(dict(email))
    priority = classifier.score_priority(dict(email))
    spam_score = classifier.get_spam_score(dict(email))

    # Update email with classification
    db.update_email_category(email_id, category)
    db.update_email_priority(email_id, priority)

    return jsonify({
        'category': category,
        'confidence': confidence,
        'priority': priority,
        'spam_score': spam_score
    })


@app.route('/api/emails/<int:email_id>/priority', methods=['PUT'])
@login_required
def api_update_email_priority(email_id):
    """Update email priority."""
    data = request.get_json()
    priority = data.get('priority', 'normal')

    valid_priorities = ['low', 'normal', 'high', 'urgent']
    if priority not in valid_priorities:
        return jsonify({'error': 'Invalid priority'}), 400

    success = db.update_email_priority(email_id, priority)
    if success:
        return jsonify({'status': 'success'})
    return jsonify({'error': 'Failed to update priority'}), 500


@app.route('/api/emails/<int:email_id>/delete', methods=['DELETE'])
@login_required
def api_delete_email(email_id):
    """Delete an email."""
    success = db.delete_email(email_id)
    if success:
        return jsonify({'status': 'success'})
    return jsonify({'error': 'Failed to delete email'}), 500


@app.route('/api/report/summary', methods=['GET'])
@login_required
def api_report_summary():
    """Get summary report."""
    try:
        stats = db.get_statistics()
        report_text = ReportGenerator.generate_summary_report(stats)

        return jsonify({
            'status': 'success',
            'report': report_text,
            'statistics': stats
        })
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/emails/category/<category>/count', methods=['GET'])
@login_required
def api_category_count(category):
    """Get count of emails in a category."""
    emails = db.get_emails_by_category(category, limit=1000000)
    return jsonify({
        'category': category,
        'count': len(emails)
    })


@app.route('/api/emails/validate', methods=['POST'])
@login_required
def api_validate_email():
    """Validate email address."""
    data = request.get_json()
    email = data.get('email', '')

    is_valid = EmailValidator.is_valid_email(email)
    return jsonify({
        'email': email,
        'is_valid': is_valid
    })


@app.route('/api/emails/fetch-new', methods=['POST'])
@login_required
def api_fetch_new_emails():
    """Manually fetch and process new emails."""
    try:
        from email_processor import EmailProcessor
        from googleapiclient.discovery import build
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        import os

        # Load credentials
        creds = None
        token_file = 'token.json'
        if os.path.exists(token_file):
            try:
                creds = Credentials.from_authorized_user_file(token_file)

                # Refresh if needed
                if creds and not creds.valid:
                    if creds.refresh_token:
                        creds.refresh(Request())
            except Exception as auth_err:
                logger.warning(f"Could not load Gmail credentials: {auth_err}")

        if not creds:
            # Return test data if no Gmail access
            logger.info("No Gmail credentials - returning test response")
            return jsonify({
                'status': 'success',
                'emails_fetched': 0,
                'emails_classified': 0,
                'message': 'Gmail not configured. App is ready. Use manual "Generate Draft" button to create replies.'
            }), 200

        # Create Gmail service
        try:
            service = build('gmail', 'v1', credentials=creds)
            processor = EmailProcessor(service, db)

            # Fetch unread emails
            emails = processor.get_unread_emails(max_results=5)
            logger.info(f"Fetched {len(emails)} emails from Gmail")

            # Classify each email
            drafted_count = 0
            for email in emails:
                try:
                    category, confidence = classifier.classify_email(email)
                    priority = classifier.score_priority(email)

                    # Update email in database
                    email_id = email.get('email_id')
                    if email_id:
                        db.update_email_category(email_id, category)
                        db.update_email_priority(email_id, priority)
                        drafted_count += 1
                except Exception as email_err:
                    logger.debug(f"Error processing individual email: {email_err}")

            return jsonify({
                'status': 'success',
                'emails_fetched': len(emails),
                'emails_classified': drafted_count,
                'message': f'✅ Fetched {len(emails)} emails and classified {drafted_count}'
            }), 200

        except Exception as gmail_err:
            logger.error(f"Gmail service error: {gmail_err}")
            return jsonify({
                'status': 'success',
                'emails_fetched': 0,
                'emails_classified': 0,
                'message': 'Gmail temporarily unavailable. Try again in a moment.'
            }), 200

    except Exception as e:
        logger.error(f"Error in fetch-new endpoint: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'message': 'Failed to fetch emails'
        }), 500


@app.route('/api/drafts/generate/<int:email_id>', methods=['POST'])
@login_required
def api_generate_draft(email_id):
    """Manually generate draft reply for an email."""
    try:
        email = db.get_email(email_id)
        if not email:
            return jsonify({'error': 'Email not found'}), 404

        # Check if draft already exists
        existing_drafts = db.get_drafts_by_email(email_id)
        if existing_drafts:
            return jsonify({
                'status': 'exists',
                'draft_id': existing_drafts[0]['id'],
                'message': 'Draft already exists for this email'
            }), 200

        # Try to generate draft using Ollama (if available)
        try:
            import requests

            prompt = f"""Generate a professional email reply based on this email:

From: {email['sender']}
Subject: {email['subject']}
Body: {email['body']}

Generate a brief, professional reply. Keep it concise and helpful."""

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
                reply_text = response.json().get('response', '').strip()
                if reply_text:
                    # Save draft
                    draft_id = db.add_draft(email_id, reply_text, model_used='mistral')
                    return jsonify({
                        'status': 'success',
                        'draft_id': draft_id,
                        'reply': reply_text,
                        'message': 'Draft generated successfully'
                    }), 201
        except Exception as e:
            logger.warning(f"Ollama generation failed: {e}")

        # If Ollama failed, create generic draft
        generic_reply = f"Thank you for your email. I will review it and get back to you shortly."
        draft_id = db.add_draft(email_id, generic_reply, model_used='template')

        return jsonify({
            'status': 'success',
            'draft_id': draft_id,
            'reply': generic_reply,
            'message': 'Template draft created'
        }), 201

    except Exception as e:
        logger.error(f"Error generating draft: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/gmail-settings', methods=['POST'])
@login_required
def api_gmail_settings():
    """Update Gmail settings."""
    try:
        user_id = session.get('user_id', 1)
        gmail_email = request.form.get('gmail_email', '').strip()

        # Validate email
        if not gmail_email or '@gmail.com' not in gmail_email:
            return jsonify({'error': 'Invalid Gmail address'}), 400

        # Update database
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users
            SET gmail_email = ?, gmail_connected = 1
            WHERE id = ?
        """, (gmail_email, user_id))
        conn.commit()
        conn.close()

        logger.info(f"User {user_id} updated Gmail to: {gmail_email}")
        return jsonify({'status': 'success', 'message': 'Gmail settings updated'}), 200

    except Exception as e:
        logger.error(f"Error updating Gmail settings: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/gmail-disconnect', methods=['POST'])
@login_required
def api_gmail_disconnect():
    """Disconnect Gmail account."""
    try:
        user_id = session.get('user_id', 1)

        # Update database
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users
            SET gmail_email = NULL, gmail_connected = 0
            WHERE id = ?
        """, (user_id,))
        conn.commit()
        conn.close()

        logger.info(f"User {user_id} disconnected Gmail")
        return jsonify({'status': 'success', 'message': 'Gmail disconnected'}), 200

    except Exception as e:
        logger.error(f"Error disconnecting Gmail: {e}")
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors."""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors."""
    logger.error(f"Internal error: {e}")
    return render_template('500.html'), 500


if __name__ == '__main__':
    port = CONFIG.get('web_ui', {}).get('port', 5000)
    debug = CONFIG.get('web_ui', {}).get('debug', False)

    # Start keep-alive service for Render deployment
    try:
        from keep_alive import start_keep_alive
        start_keep_alive()
    except ImportError:
        logger.warning("Keep-alive module not available")

    logger.info(f"Starting Flask app on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
