# Email Assistant - Configuration Guide

**Version**: 2.0
**Last Updated**: March 27, 2026

---

## Overview

The Email Assistant uses a hierarchical configuration system:

1. **Default values** - Built into code
2. **config.json** - Project-specific settings (highest priority)
3. **Environment variables** - System-level overrides (coming soon)

This guide covers all available configuration options.

---

## Configuration File Structure

Create `config.json` in project root with this structure:

```json
{
  "gmail": { ... },
  "database": { ... },
  "llm": { ... },
  "web": { ... },
  "notifications": { ... },
  "logging": { ... },
  "security": { ... },
  "scheduler": { ... }
}
```

---

## Gmail Configuration

### Location
```json
"gmail": {
  "credentials_file": "credentials.json",
  "token_file": "token.json",
  "scopes": [...],
  "user_id": "me"
}
```

### Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `credentials_file` | string | `credentials.json` | Path to Gmail OAuth credentials JSON |
| `token_file` | string | `token.json` | Path to cached OAuth token |
| `user_id` | string | `"me"` | Gmail user ID (use "me" for authenticated user) |
| `scopes` | array | See below | OAuth permission scopes |

### Scopes

Required scopes for full functionality:

```json
"scopes": [
  "https://www.googleapis.com/auth/gmail.readonly",
  "https://www.googleapis.com/auth/gmail.modify"
]
```

**Scope Meanings**:
- `gmail.readonly` - Read emails, drafts, labels
- `gmail.modify` - Send, modify, delete emails

### Example

```json
"gmail": {
  "credentials_file": "/secure/gmail_credentials.json",
  "token_file": "/secure/gmail_token.json",
  "scopes": [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify"
  ],
  "user_id": "me"
}
```

---

## Database Configuration

### Location
```json
"database": {
  "file": "email_assistant.db",
  "backup_dir": "./backups",
  "vacuum_interval_days": 7,
  "connection_timeout": 30
}
```

### Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `file` | string | `email_assistant.db` | SQLite database file path |
| `backup_dir` | string | `./backups` | Directory for automatic backups |
| `vacuum_interval_days` | int | `7` | Days between automatic VACUUM operations |
| `connection_timeout` | int | `30` | Connection timeout in seconds |
| `journal_mode` | string | `WAL` | SQLite journal mode (WAL for concurrency) |
| `synchronous` | string | `NORMAL` | Sync level (NORMAL, FULL, OFF) |

### Example

```json
"database": {
  "file": "/data/email_assistant.db",
  "backup_dir": "/backups/email_assistant",
  "vacuum_interval_days": 7,
  "connection_timeout": 30,
  "journal_mode": "WAL",
  "synchronous": "NORMAL"
}
```

### Journal Mode Options

- `WAL` (recommended) - Write-Ahead Logging, better concurrency
- `DELETE` - Simpler, lower performance
- `TRUNCATE` - Faster than DELETE
- `PERSIST` - Reduces I/O

### Synchronous Options

- `OFF` - Fastest, least safe (power loss risk)
- `NORMAL` - Balanced (recommended)
- `FULL` - Safest, slowest

---

## LLM Configuration

### Location
```json
"llm": {
  "primary_provider": "claude",
  "fallback_provider": "ollama",
  "claude_api_key": "sk-...",
  "claude_model": "claude-3-5-sonnet-20241022",
  "claude_timeout": 30,
  "ollama_base_url": "http://localhost:11434",
  "ollama_model": "mistral:latest",
  "ollama_timeout": 60,
  "ollama_max_retries": 3,
  "circuit_breaker_threshold": 3,
  "circuit_breaker_timeout_seconds": 300
}
```

### Claude Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `primary_provider` | string | `claude` | Primary LLM provider |
| `claude_api_key` | string | - | Claude API key (sk-...) |
| `claude_model` | string | `claude-3-5-sonnet-20241022` | Claude model to use |
| `claude_timeout` | int | `30` | Request timeout in seconds |
| `claude_temperature` | float | `0.7` | Response creativity (0-1) |
| `claude_max_tokens` | int | `1024` | Max tokens in response |

### Ollama Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `ollama_base_url` | string | `http://localhost:11434` | Ollama server URL |
| `ollama_model` | string | `mistral:latest` | Ollama model to use |
| `ollama_timeout` | int | `60` | Request timeout in seconds |
| `ollama_max_retries` | int | `3` | Retry attempts |
| `ollama_temperature` | float | `0.7` | Response creativity |

### Circuit Breaker

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `circuit_breaker_threshold` | int | `3` | Failures before opening circuit |
| `circuit_breaker_timeout_seconds` | int | `300` | Seconds before reset attempt |
| `circuit_breaker_on_timeout` | bool | `true` | Count timeouts as failures |

### Example

```json
"llm": {
  "primary_provider": "claude",
  "fallback_provider": "ollama",
  "claude_api_key": "sk-proj-abc123...",
  "claude_model": "claude-3-5-sonnet-20241022",
  "claude_timeout": 30,
  "claude_temperature": 0.7,
  "claude_max_tokens": 1024,
  "ollama_base_url": "http://localhost:11434",
  "ollama_model": "mistral:latest",
  "ollama_timeout": 60,
  "ollama_max_retries": 3,
  "circuit_breaker_threshold": 3,
  "circuit_breaker_timeout_seconds": 300
}
```

---

## Web Configuration

### Location
```json
"web": {
  "host": "0.0.0.0",
  "port": 5000,
  "debug": false,
  "username": "admin",
  "password_hash": "...",
  "session_cookie_secure": true,
  "session_cookie_samesite": "Strict",
  "session_cookie_httponly": true,
  "session_timeout_minutes": 60,
  "enable_csrf": true,
  "enable_rate_limiting": true,
  "rate_limit": "5 per minute"
}
```

### Server Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `host` | string | `0.0.0.0` | Listen address (0.0.0.0 for all interfaces) |
| `port` | int | `5000` | Port number |
| `debug` | bool | `false` | Flask debug mode (never enable in production) |
| `threaded` | bool | `true` | Enable threading |
| `workers` | int | `4` | Number of worker processes (production) |

### Authentication

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `username` | string | `admin` | Web UI username |
| `password_hash` | string | - | Bcrypt password hash (generated by migrate_passwords.py) |
| `session_timeout_minutes` | int | `60` | Session expiration time |

### Security

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `session_cookie_secure` | bool | `true` | Require HTTPS for cookie |
| `session_cookie_samesite` | string | `Strict` | SameSite cookie policy |
| `session_cookie_httponly` | bool | `true` | Block JavaScript cookie access |
| `enable_csrf` | bool | `true` | Enable CSRF protection |
| `enable_rate_limiting` | bool | `true` | Enable rate limiting |
| `rate_limit` | string | `5 per minute` | Rate limit rule |

### Example

```json
"web": {
  "host": "127.0.0.1",
  "port": 5000,
  "debug": false,
  "username": "admin",
  "password_hash": "$2b$12$...",
  "session_cookie_secure": true,
  "session_cookie_samesite": "Strict",
  "session_cookie_httponly": true,
  "session_timeout_minutes": 60,
  "enable_csrf": true,
  "enable_rate_limiting": true,
  "rate_limit": "5 per minute"
}
```

---

## Notifications Configuration

### Location
```json
"notifications": {
  "enabled": true,
  "desktop_notifications": true,
  "notify_urgent": true,
  "notify_important": true,
  "notify_normal": false,
  "quiet_hours_enabled": true,
  "quiet_hours_start": "22:00",
  "quiet_hours_end": "08:00",
  "daily_digest_enabled": false,
  "daily_digest_time": "09:00"
}
```

### Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `enabled` | bool | `true` | Enable all notifications |
| `desktop_notifications` | bool | `true` | Use system notifications |
| `notify_urgent` | bool | `true` | Notify on urgent emails |
| `notify_important` | bool | `true` | Notify on important emails |
| `notify_normal` | bool | `false` | Notify on normal emails |
| `notify_low` | bool | `false` | Notify on low priority emails |
| `quiet_hours_enabled` | bool | `true` | Enable quiet hours |
| `quiet_hours_start` | string | `22:00` | Quiet hours start time (HH:MM) |
| `quiet_hours_end` | string | `08:00` | Quiet hours end time (HH:MM) |
| `daily_digest_enabled` | bool | `false` | Send daily email digest |
| `daily_digest_time` | string | `09:00` | Digest delivery time (HH:MM) |

### Example

```json
"notifications": {
  "enabled": true,
  "desktop_notifications": true,
  "notify_urgent": true,
  "notify_important": true,
  "notify_normal": false,
  "quiet_hours_enabled": true,
  "quiet_hours_start": "22:00",
  "quiet_hours_end": "08:00",
  "daily_digest_enabled": false,
  "daily_digest_time": "09:00"
}
```

---

## Logging Configuration

### Location
```json
"logging": {
  "level": "INFO",
  "file": "email_assistant.log",
  "max_size_mb": 10,
  "backup_count": 5,
  "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
}
```

### Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `level` | string | `INFO` | Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `file` | string | `email_assistant.log` | Log file path |
| `max_size_mb` | int | `10` | Max log file size before rotation |
| `backup_count` | int | `5` | Number of backup files to keep |
| `format` | string | See default | Log message format |
| `console` | bool | `true` | Also log to console |

### Log Levels

- `DEBUG` - Detailed diagnostic information
- `INFO` - General informational messages (recommended)
- `WARNING` - Warning messages (issues to investigate)
- `ERROR` - Error messages (failures, exceptions)
- `CRITICAL` - Critical errors (system will likely fail)

### Example

```json
"logging": {
  "level": "INFO",
  "file": "/var/log/email_assistant.log",
  "max_size_mb": 50,
  "backup_count": 10,
  "format": "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
  "console": true
}
```

---

## Security Configuration

### Location
```json
"security": {
  "enable_https": false,
  "ssl_cert_path": "/path/to/cert.pem",
  "ssl_key_path": "/path/to/key.pem",
  "allowed_hosts": ["localhost", "127.0.0.1"],
  "encryption_key": "...",
  "session_secret_key": "..."
}
```

### Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `enable_https` | bool | `false` | Use HTTPS (requires certificates) |
| `ssl_cert_path` | string | - | Path to SSL certificate file |
| `ssl_key_path` | string | - | Path to SSL key file |
| `allowed_hosts` | array | `[localhost]` | Allowed host names |
| `encryption_key` | string | - | Fernet key for token encryption |
| `session_secret_key` | string | - | Flask session secret key |

### Generate Encryption Keys

```bash
# Generate Fernet key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Generate session secret
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### SSL Certificate Generation

```bash
# Generate self-signed certificate (testing only)
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

# For production, use Let's Encrypt or other CA
```

### Example

```json
"security": {
  "enable_https": true,
  "ssl_cert_path": "/etc/ssl/certs/email_assistant.pem",
  "ssl_key_path": "/etc/ssl/private/email_assistant.key",
  "allowed_hosts": ["email.example.com", "localhost"],
  "encryption_key": "Fz6e...",
  "session_secret_key": "super-secret-key-here"
}
```

---

## Scheduler Configuration

### Location
```json
"scheduler": {
  "enabled": true,
  "check_interval": 60,
  "max_concurrent_sends": 5,
  "retry_failed_attempts": 3,
  "retry_delay_seconds": 300
}
```

### Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `enabled` | bool | `true` | Enable background scheduler |
| `check_interval` | int | `60` | Seconds between checks |
| `max_concurrent_sends` | int | `5` | Max emails sending simultaneously |
| `retry_failed_attempts` | int | `3` | Retry attempts for failed sends |
| `retry_delay_seconds` | int | `300` | Seconds between retry attempts |

### Example

```json
"scheduler": {
  "enabled": true,
  "check_interval": 60,
  "max_concurrent_sends": 5,
  "retry_failed_attempts": 3,
  "retry_delay_seconds": 300
}
```

---

## Complete Example Configuration

```json
{
  "gmail": {
    "credentials_file": "credentials.json",
    "token_file": "token.json",
    "scopes": [
      "https://www.googleapis.com/auth/gmail.readonly",
      "https://www.googleapis.com/auth/gmail.modify"
    ],
    "user_id": "me"
  },
  "database": {
    "file": "email_assistant.db",
    "backup_dir": "./backups",
    "vacuum_interval_days": 7,
    "connection_timeout": 30,
    "journal_mode": "WAL",
    "synchronous": "NORMAL"
  },
  "llm": {
    "primary_provider": "claude",
    "fallback_provider": "ollama",
    "claude_api_key": "sk-proj-...",
    "claude_model": "claude-3-5-sonnet-20241022",
    "claude_timeout": 30,
    "claude_temperature": 0.7,
    "claude_max_tokens": 1024,
    "ollama_base_url": "http://localhost:11434",
    "ollama_model": "mistral:latest",
    "ollama_timeout": 60,
    "ollama_max_retries": 3,
    "circuit_breaker_threshold": 3,
    "circuit_breaker_timeout_seconds": 300
  },
  "web": {
    "host": "0.0.0.0",
    "port": 5000,
    "debug": false,
    "username": "admin",
    "password_hash": "$2b$12$...",
    "session_cookie_secure": true,
    "session_cookie_samesite": "Strict",
    "session_cookie_httponly": true,
    "session_timeout_minutes": 60,
    "enable_csrf": true,
    "enable_rate_limiting": true,
    "rate_limit": "5 per minute"
  },
  "notifications": {
    "enabled": true,
    "desktop_notifications": true,
    "notify_urgent": true,
    "notify_important": true,
    "notify_normal": false,
    "quiet_hours_enabled": true,
    "quiet_hours_start": "22:00",
    "quiet_hours_end": "08:00",
    "daily_digest_enabled": false,
    "daily_digest_time": "09:00"
  },
  "logging": {
    "level": "INFO",
    "file": "email_assistant.log",
    "max_size_mb": 10,
    "backup_count": 5,
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "console": true
  },
  "security": {
    "enable_https": false,
    "ssl_cert_path": "/path/to/cert.pem",
    "ssl_key_path": "/path/to/key.pem",
    "allowed_hosts": ["localhost", "127.0.0.1"],
    "encryption_key": "...",
    "session_secret_key": "..."
  },
  "scheduler": {
    "enabled": true,
    "check_interval": 60,
    "max_concurrent_sends": 5,
    "retry_failed_attempts": 3,
    "retry_delay_seconds": 300
  }
}
```

---

## Environment Variables

You can override config values with environment variables:

```bash
# Email assistant config
export GMAIL_CREDENTIALS_FILE=/secure/credentials.json
export DATABASE_FILE=/data/email_assistant.db
export CLAUDE_API_KEY=sk-proj-...
export WEB_HOST=0.0.0.0
export WEB_PORT=5000
export LOG_LEVEL=INFO
```

---

## Quick Configuration Templates

### Development Setup
```json
{
  "web": {
    "debug": true,
    "host": "127.0.0.1",
    "port": 5000
  },
  "logging": {
    "level": "DEBUG",
    "console": true
  }
}
```

### Production Setup
```json
{
  "web": {
    "debug": false,
    "host": "0.0.0.0",
    "port": 5000,
    "enable_https": true
  },
  "logging": {
    "level": "INFO",
    "file": "/var/log/email_assistant.log"
  },
  "security": {
    "enable_https": true,
    "ssl_cert_path": "/etc/ssl/certs/email_assistant.pem",
    "ssl_key_path": "/etc/ssl/private/email_assistant.key"
  }
}
```

### Low-Resource Setup
```json
{
  "llm": {
    "ollama_model": "phi:latest",
    "circuit_breaker_threshold": 1
  },
  "scheduler": {
    "check_interval": 300,
    "max_concurrent_sends": 1
  }
}
```

---

## Configuration Validation

After creating config.json, validate:

```bash
python -c "
import json
with open('config.json') as f:
    config = json.load(f)
print('✓ Configuration is valid JSON')
print(f'✓ Database: {config[\"database\"][\"file\"]}')
print(f'✓ LLM provider: {config[\"llm\"][\"primary_provider\"]}')
"
```

---

## Troubleshooting Configuration

### Cannot find credentials.json
```
Error: credentials.json not found
Solution: Run Gmail OAuth setup (see DEPLOYMENT_GUIDE.md)
```

### Invalid password hash
```
Error: Config contains plain text password
Solution: Run: python migrate_passwords.py
```

### Database locked
```
Error: database is locked
Solution: Check journal_mode (use WAL) and connection_timeout
```

### LLM provider not connecting
```
Check:
- API key validity (claude_api_key)
- Ollama server running (ollama_base_url)
- Network connectivity
- Firewall rules
```

---

**Configuration Guide Version**: 1.0
**Last Updated**: March 27, 2026
**Maintained By**: Email Assistant Team
