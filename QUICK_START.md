# Email Assistant - Quick Start Guide

**Get Started in 5 Minutes**

---

## 1. Install Dependencies (1 min)

```bash
# Navigate to project directory
cd C:\Users\awais

# Install required packages
pip install -r requirements.txt
```

---

## 2. Setup Gmail OAuth (2 min)

1. Go to https://console.cloud.google.com/
2. Create new project → "Email Assistant"
3. Search for "Gmail API" → Enable it
4. Create credentials (OAuth 2.0 Desktop app)
5. Download JSON → Save as `credentials.json` in project root

---

## 3. Generate Password (1 min)

```bash
python migrate_passwords.py
```

When prompted:
- Enter new username (default: `admin`)
- Enter new password (make it strong!)

This updates `config.json` with bcrypt hash.

---

## 4. Start the Application (1 min)

**Terminal 1 - Web Server:**
```bash
python -c "from web_ui.app import app; app.run(debug=True, host='127.0.0.1', port=5000)"
```

**Terminal 2 - Email Processor:**
```bash
python main.py
```

---

## 5. Access the Web UI

Open browser: **http://localhost:5000**

Login with credentials from step 3.

---

## What You Can Do

### ✉️ Email Management
- View all emails from Gmail
- Mark as read/unread
- Search with full-text search
- Filter by sender, priority, date
- View email threads (conversations)

### 📝 Smart Replies
- Auto-generate AI replies using Claude
- Fallback to Ollama if Claude unavailable
- Template fallback as last resort
- Create and edit drafts

### 📎 Attachments
- View attachment list
- Download attachments
- See preview for images/PDFs
- Get attachment context for AI

### 🔔 Notifications
- Get desktop notifications
- Quiet hours support (no notifications 22:00-08:00)
- Configure by priority level

### ⏰ Schedule & Snooze
- Schedule drafts to send later
- Snooze emails until specific time
- Background scheduler processes automatically

### 🔍 Advanced Search
- Search across all emails
- Save frequently used searches
- Filter by multiple criteria

---

## Common Tasks

### Generate Reply for Email

1. Click email to open
2. Click "Generate Reply"
3. Edit if needed
4. Click "Save Draft" or "Send"

### Schedule Email for Later

1. Create draft
2. Click "Schedule"
3. Pick date and time
4. Confirm

### Snooze Email Until Tomorrow

1. Open email
2. Click "Snooze"
3. Select "Tomorrow at 9 AM"
4. Email reappears in inbox tomorrow

### Search for Important Emails

1. Click "Search"
2. Enter: `urgent meeting`
3. Or use advanced filters:
   - Sender: john@example.com
   - Priority: High
   - Date: Last 7 days

### Save a Search

1. Run search
2. Click "Save This Search"
3. Name it: "Work Urgent"
4. Reuse anytime from "Saved Searches"

---

## File Structure

```
C:\Users\awais\
├── web_ui/
│   └── app.py                 # Flask web server
├── main.py                    # Email processor
├── database.py                # Database management
├── llm_manager.py            # AI reply generation
├── thread_manager.py         # Email threading
├── search_engine.py          # Search functionality
├── attachment_manager.py     # Attachment handling
├── notification_manager.py   # Notifications
├── email_scheduler.py        # Scheduling/snooze
├── auth_utils.py             # Password hashing
├── validators.py             # Input validation
├── config.json               # Configuration (create this)
├── credentials.json          # Gmail OAuth (download this)
├── email_assistant.db        # Database (auto-created)
└── email_assistant.log       # Logs (auto-created)
```

---

## Troubleshooting

### Can't login
```
- Check username/password from migrate_passwords.py
- Try again (rate limited to 5 attempts/minute)
```

### No emails showing
```
- Check Gmail OAuth setup (credentials.json exists?)
- Run: python main.py --verbose
- Check logs: email_assistant.log
```

### AI replies not generating
```
- Check Claude API key in config.json
- Or ensure Ollama running on http://localhost:11434
- Check logs for error messages
```

### Database errors
```
- Delete email_assistant.db
- Restart application (recreates database)
- Verify database.py can create tables
```

### Notifications not working
```
- Ensure desktop_notifications=true in config.json
- Check quiet hours (22:00-08:00 suppresses notifications)
- Windows 10+ required for desktop notifications
```

---

## Next Steps

1. **Explore Features** - Try all UI features
2. **Read Docs** - See API_DOCUMENTATION.md for API
3. **Configure** - Customize config.json settings
4. **Deploy** - See DEPLOYMENT_GUIDE.md for production setup

---

## Help & Support

- **Logs**: `email_assistant.log`
- **Config**: See `CONFIGURATION_GUIDE.md`
- **API**: See `API_DOCUMENTATION.md`
- **Deployment**: See `DEPLOYMENT_GUIDE.md`

---

**Quick Start Guide v1.0**
**Last Updated**: March 27, 2026
