# Email Assistant - Deployment Guide

**Status**: Production-Ready
**Version**: 2.0
**Last Updated**: March 27, 2026

---

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Database Setup](#database-setup)
5. [Security Hardening](#security-hardening)
6. [Running the Application](#running-the-application)
7. [Monitoring and Health Checks](#monitoring-and-health-checks)
8. [Troubleshooting](#troubleshooting)
9. [Backup and Recovery](#backup-and-recovery)

---

## Pre-Deployment Checklist

Before deploying to production, verify:

- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] `config.json` created with valid credentials
- [ ] Gmail OAuth credentials configured
- [ ] Database initialized and migrated
- [ ] All tests passing (`python tests_comprehensive.py`)
- [ ] HTTPS certificate obtained (for production)
- [ ] Firewall rules configured
- [ ] Backup location configured
- [ ] Monitoring alerts set up
- [ ] Logging directory writable
- [ ] Python 3.8+ installed

---

## Installation

### 1. Clone and Setup Environment

```bash
# Navigate to project directory
cd C:\Users\awais  # or your project path

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Install System Dependencies

**Windows:**
```bash
# Optional: For desktop notifications (Windows 10+)
# win10toast is already in requirements.txt
```

**Linux/macOS:**
```bash
# For SQLite development headers
sudo apt-get install libsqlite3-dev  # Ubuntu/Debian
brew install sqlite                   # macOS
```

### 3. Verify Installation

```bash
python -c "from llm_manager import LLMManager; from thread_manager import ThreadManager; from search_engine import EmailSearchEngine; print('✓ All modules installed successfully')"
```

---

## Configuration

### 1. Create Configuration File

Create `config.json` in project root with the following structure:

```json
{
  "gmail": {
    "credentials_file": "credentials.json",
    "token_file": "token.json",
    "scopes": ["https://www.googleapis.com/auth/gmail.readonly", "https://www.googleapis.com/auth/gmail.modify"],
    "user_id": "me"
  },
  "database": {
    "file": "email_assistant.db",
    "backup_dir": "./backups",
    "vacuum_interval_days": 7
  },
  "llm": {
    "primary_provider": "claude",
    "fallback_provider": "ollama",
    "claude_api_key": "sk-...",
    "ollama_base_url": "http://localhost:11434",
    "ollama_model": "mistral:latest",
    "circuit_breaker_threshold": 3,
    "circuit_breaker_timeout_seconds": 300
  },
  "web": {
    "host": "0.0.0.0",
    "port": 5000,
    "debug": false,
    "username": "admin",
    "password_hash": "hash_generated_by_migrate_passwords.py",
    "session_cookie_secure": true,
    "session_cookie_samesite": "Strict",
    "session_timeout_minutes": 60,
    "enable_csrf": true,
    "enable_rate_limiting": true,
    "rate_limit": "5 per minute"
  },
  "notifications": {
    "enabled": true,
    "desktop_notifications": true,
    "quiet_hours_start": "22:00",
    "quiet_hours_end": "08:00"
  },
  "logging": {
    "level": "INFO",
    "file": "email_assistant.log",
    "max_size_mb": 10,
    "backup_count": 5
  },
  "security": {
    "enable_https": true,
    "ssl_cert_path": "/path/to/cert.pem",
    "ssl_key_path": "/path/to/key.pem",
    "allowed_hosts": ["localhost", "127.0.0.1"]
  }
}
```

### 2. Generate Password Hash

```bash
python migrate_passwords.py
```

This will prompt you for a new password and update `config.json` with the bcrypt hash.

### 3. Setup Gmail OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Gmail API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download JSON and save as `credentials.json`

First run will prompt for authentication:
```bash
python main.py
# Browser will open for Gmail authorization
# Grant permissions when prompted
```

---

## Database Setup

### 1. Initialize Database

```bash
python -c "from database import DatabaseManager; db = DatabaseManager(); print('✓ Database initialized successfully')"
```

This creates:
- `users` table
- `emails` table
- `drafts` table
- `email_threads` table (for threading)
- `saved_searches` table (for search)
- `attachments` table (for attachments)
- `scheduled_emails` table (for scheduling)
- `snoozed_emails` table (for snooze)
- `notification_preferences` table (for notifications)
- Default user with ID=1

### 2. Backup Database

```bash
# Manual backup
cp email_assistant.db email_assistant.db.backup

# Or use backup script
python -c "from database import DatabaseManager; db = DatabaseManager(); db.backup()"
```

### 3. Database Optimization

Periodically run VACUUM to optimize database:

```bash
python -c "from database import DatabaseManager; db = DatabaseManager(); db.vacuum()"
```

---

## Security Hardening

### 1. Password Security

- ✅ All passwords hashed with bcrypt (12 rounds)
- ✅ Never store plain text passwords
- Use strong passwords (12+ characters, mixed case, numbers, symbols)

```bash
python migrate_passwords.py  # Update password securely
```

### 2. CSRF Protection

- ✅ Flask-WTF enabled by default
- ✅ CSRF tokens on all forms
- Session cookies marked HttpOnly

### 3. Rate Limiting

- ✅ Login endpoint: 5 attempts per minute
- ✅ Other endpoints: configurable via config.json
- Prevents brute force attacks

### 4. HTTPS/SSL

For production deployment:

```bash
# Generate self-signed certificate (testing only)
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

# Update config.json
{
  "security": {
    "enable_https": true,
    "ssl_cert_path": "/path/to/cert.pem",
    "ssl_key_path": "/path/to/key.pem"
  }
}
```

### 5. OAuth Token Encryption

OAuth tokens are encrypted in database using Fernet symmetric encryption.

### 6. Input Validation

All user inputs validated:
- Email addresses checked with regex
- Strings sanitized against XSS
- Priority/status values whitelisted
- SQL injection prevented via parameterized queries

### 7. Session Security

```json
{
  "web": {
    "session_cookie_secure": true,
    "session_cookie_samesite": "Strict",
    "session_cookie_httponly": true,
    "session_timeout_minutes": 60
  }
}
```

---

## Running the Application

### Development

```bash
# Terminal 1: Start Flask web server
python -c "from web_ui.app import app; app.run(debug=True, host='127.0.0.1', port=5000)"

# Terminal 2: Start background email processor
python main.py --user-id=1 --check-interval=300
```

Access at: `http://localhost:5000`

### Production

```bash
# Using Gunicorn (recommended)
pip install gunicorn

gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 web_ui.app:app

# In separate terminal, run email processor
python main.py --user-id=1 --check-interval=300 --background
```

### Docker (Optional)

See `Dockerfile` for containerized deployment.

---

## Monitoring and Health Checks

### 1. Check Application Status

```bash
# Database connectivity
python -c "from database import DatabaseManager; db = DatabaseManager(); print(f'✓ Database OK: {db.get_email_count(1)} emails')"

# LLM providers
python -c "from llm_manager import LLMManager; llm = LLMManager({}); print(llm.get_provider_status())"

# Email processor
curl http://localhost:5000/api/health
```

### 2. Logging

Check application logs:

```bash
# Real-time logs
tail -f email_assistant.log

# Last 100 lines with errors
grep ERROR email_assistant.log | tail -100

# Rotate logs (handled automatically)
```

### 3. Performance Monitoring

```bash
# Check database size
ls -lh email_assistant.db

# Monitor process
ps aux | grep python

# Check memory/CPU
top -p $(pgrep -f 'python main.py')
```

### 4. Alerts to Configure

- [ ] Low disk space warning
- [ ] Database size exceeding limit
- [ ] LLM provider failures (circuit breaker open)
- [ ] Email processing delays
- [ ] Failed OAuth token refresh
- [ ] High error rate in logs

---

## Troubleshooting

### Database Connection Issues

```python
# Test connection
from database import DatabaseManager
db = DatabaseManager()
with db.get_connection_context() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM emails")
    print(cursor.fetchone())
```

### Gmail API Errors

```bash
# Re-authenticate
rm token.json
python main.py  # Will prompt for re-authentication

# Check credentials
python -c "from email_processor import EmailProcessor; ep = EmailProcessor(); print('✓ Gmail API connected')"
```

### LLM Provider Failures

```python
# Check provider status
from llm_manager import LLMManager
llm = LLMManager({})
status = llm.get_provider_status()
print(status)

# Reset circuit breaker
llm.claude_circuit_open = False
llm.claude_failures = 0
```

### Search Not Working

```bash
# Rebuild search indexes
python -c "
from database import DatabaseManager
from search_engine import EmailSearchEngine
db = DatabaseManager()
search = EmailSearchEngine(db)
search._build_search_index(1)  # For user_id=1
"
```

### Performance Issues

```bash
# Optimize database
python -c "from database import DatabaseManager; DatabaseManager().vacuum()"

# Check slow queries
grep 'took.*ms' email_assistant.log | sort -k2 -rn | head -20
```

---

## Backup and Recovery

### 1. Automated Backups

Backups happen automatically based on `database.backup_dir` setting.

### 2. Manual Backup

```bash
# Single backup
cp email_assistant.db email_assistant.db.$(date +%Y%m%d_%H%M%S).backup

# Backup with compression
tar -czf email_assistant_backup_$(date +%Y%m%d).tar.gz email_assistant.db email_assistant.log
```

### 3. Restore from Backup

```bash
# From backup file
cp email_assistant.db.backup email_assistant.db

# Verify integrity
sqlite3 email_assistant.db "PRAGMA integrity_check;"
```

### 4. Database Export

```bash
# Export to CSV
python -c "
from database import DatabaseManager
db = DatabaseManager()
import csv
with db.get_connection_context() as conn:
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM emails WHERE user_id=1')
    with open('emails_export.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(cursor.fetchall())
"
```

---

## Upgrade Path

### From Previous Version

If upgrading from earlier version:

```bash
# 1. Backup current database
cp email_assistant.db email_assistant.db.backup

# 2. Install new requirements
pip install -r requirements.txt

# 3. Update database schema
python -c "from database import DatabaseManager; DatabaseManager().upgrade()"

# 4. Migrate passwords
python migrate_passwords.py

# 5. Run tests
python tests_comprehensive.py

# 6. Restart application
```

---

## Production Checklist

- [ ] All environment variables set
- [ ] Database backed up
- [ ] HTTPS certificates valid
- [ ] Password changed from defaults
- [ ] Logging configured
- [ ] Rate limiting enabled
- [ ] CSRF protection enabled
- [ ] Session security enabled
- [ ] OAuth tokens encrypted
- [ ] All tests passing
- [ ] Monitoring alerts set up
- [ ] Backup schedule configured
- [ ] Admin documentation reviewed
- [ ] Support contact information documented

---

## Support and Troubleshooting

For issues:

1. Check logs: `email_assistant.log`
2. Run diagnostics: `python tests_comprehensive.py`
3. Review configuration: `config.json`
4. Check database: `sqlite3 email_assistant.db .schema`

For detailed API documentation, see `API_DOCUMENTATION.md`

---

**Deployment Guide Version**: 1.0
**Last Updated**: March 27, 2026
**Maintained By**: Email Assistant Team
