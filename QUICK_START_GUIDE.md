# 📧 Email Assistant - Complete Step-by-Step Setup Guide

## Table of Contents
1. [Prerequisites Check](#prerequisites-check)
2. [Installation](#installation)
3. [Running the System](#running-the-system)
4. [Accessing the Web Interface](#accessing-the-web-interface)
5. [Using Each Feature](#using-each-feature)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites Check

### ✅ What You Need

Before starting, make sure you have:

1. **Python 3.8 or higher**
   ```bash
   python --version
   ```
   Should show version 3.8+

2. **Ollama Running**
   - Download from: https://ollama.ai
   - After installation, open terminal and run:
   ```bash
   ollama serve
   ```
   Keep this running in background. You'll see: `Serving on 127.0.0.1:11434`

3. **Gmail Credentials** (Already set up from before)
   - You should have `credentials.json` in `C:\Users\awais\`
   - You should have `gmail_token.pickle` already (if not, first run will generate it)

4. **All Files** from the new implementation
   - All the .py files in `C:\Users\awais\`
   - `web_ui/` folder with templates and static files

---

## Installation

### Step 1: Install Python Packages

Open Command Prompt or PowerShell in `C:\Users\awais\` directory:

```bash
cd C:\Users\awais
pip install -r requirements.txt
```

**Expected output:** Should see "Successfully installed" messages for:
- Flask
- flask-cors
- langdetect
- And other dependencies

⏱️ **Takes 2-3 minutes**

### Step 2: Verify Installation

```bash
python -c "import flask; import ollama_integration; print('All packages installed!')"
```

Should print: `All packages installed!`

---

## Running the System

You'll need **2 Terminal Windows** open:

### Terminal 1: Run Ollama (Keep running)

```bash
ollama serve
```

**Expected Output:**
```
Serving on 127.0.0.1:11434
```

✅ Leave this running. Don't close it.

---

### Terminal 2: Run Email Assistant

First, navigate to the project directory:

```bash
cd C:\Users\awais
```

#### Option A: Run Only Web UI (Recommended for testing)

```bash
python web_ui/app.py
```

**Expected Output:**
```
[INFO] Starting Flask app on port 5000
WARNING: This is a development server...
Running on http://127.0.0.1:5000/
```

✅ The web UI will be available at `http://127.0.0.1:5000`

#### Option B: Run Email Processing + Web UI (Production)

In a 3rd terminal:

```bash
cd C:\Users\awais
python main.py
```

This will:
- Monitor Gmail for unread emails every 5 minutes
- Generate replies using Ollama
- Create Gmail drafts
- Log everything

---

## Accessing the Web Interface

### Step 1: Open Browser

Go to: **http://127.0.0.1:5000**

You'll see the login page with a lock icon.

### Step 2: Login

**Default Password:** `admin`

⚠️ **CHANGE THIS!** Edit `config.json`:
```json
"web_ui": {
    "password": "your-new-password"
}
```

### Step 3: You're In!

You'll see the **Dashboard** with:
- 📊 Total emails
- ✓ Processed count
- 📝 Pending drafts
- 📈 Category chart

---

## Using Each Feature

### 📧 Feature 1: Dashboard

**Location:** Click "Dashboard" in navbar or go to `http://127.0.0.1:5000/dashboard`

**What you see:**
- Total unread emails count
- How many you've already processed
- Pending drafts waiting for review
- Email categories pie chart
- Service health status (✓ = good, ⚠ = issues)

**What to do:**
- Stats update automatically every 30 seconds
- Green ✓ = Gmail, Ollama, Database are working
- Red ✗ = Something needs attention

---

### 📬 Feature 2: View All Emails

**Location:** Click "Emails" in navbar

**What you see:**
- List of all emails in database
- From, Subject, Category, Priority, Date
- Which ones are processed (✓ or ✗)

**How to use:**
1. **Filter by category:**
   - Click dropdown "All Categories"
   - Select: Personal, Work, Support, Marketing, Bills, etc.
   - List filters automatically

2. **View details:**
   - Hover over a row to see it highlight
   - Click to see full email

**Example:**
- From: john@example.com
- Subject: Project Update
- Category: work (blue badge)
- Priority: high (yellow badge)
- Processed: ✓ Yes

---

### ✍️ Feature 3: Review & Edit Drafts

**Location:** Click "Drafts" in navbar

**This is the MOST IMPORTANT feature!**

**What you see:**
- All AI-generated reply drafts
- Original email on left
- Generated reply on right
- Confidence score (how good is the reply)

**Example view:**
```
┌─────────────────────────────────────────┐
│ From: customer@example.com              │
│ Subject: Need help with order           │
├─────────────────────┬───────────────────┤
│ ORIGINAL EMAIL      │ GENERATED REPLY   │
├─────────────────────┤                   │
│ Hi, I have a        │ Hi there,         │
│ question about      │                   │
│ my order...         │ Thank you for     │
│                     │ contacting us...  │
│                     │                   │
│ [Confidence: 85%]   │                   │
└─────────────────────┴───────────────────┘
```

### How to Manage Drafts:

#### ✓ APPROVE Draft
1. Click **"✓ Approve"** button
2. Draft moves to Gmail as draft (not sent!)
3. Go check your Gmail - draft is there
4. You can edit & send from Gmail

#### ✎ EDIT Draft
1. Click **"✎ Edit"** button
2. Modal pops up with text box
3. Make changes to reply
4. Click **"Save Changes"**
5. Changes saved to database

#### 🔄 REGENERATE
1. Click **"🔄 Regenerate"** button
2. System creates new reply using Ollama
3. If you don't like first version, get a new one
4. Use this to try different tone/style

#### 🔗 OPEN IN GMAIL
1. Click **"🔗 Gmail"** button
2. It tells you the Draft ID
3. Open Gmail and find your drafts folder
4. Edit and send from there

#### ✕ DELETE
1. Click **"✕ Delete"** button
2. Confirm deletion
3. Draft removed (can't undo!)

---

### 📊 Feature 4: Analytics Dashboard

**Location:** Click "Analytics" in navbar

**What you see:**
- Today's email count
- How many processed
- Processing percentage
- Category distribution chart
- 30-day trend line
- Response time average

**Example stats:**
```
Today's Emails: 15
Processed Today: 12
Processing Rate: 80%
Avg Response: 2.5 hours

Categories:
Work: 8 emails
Personal: 4 emails
Support: 2 emails
Marketing: 1 email
```

**How to use:**
- **Chart 1 (Bar):** Shows which categories have most emails
- **Chart 2 (Line):** Shows trends over 30 days
- Helps you see patterns in email volume

---

### 📝 Feature 5: Templates

**Location:** Click "Templates" in navbar

**What are templates?**
Pre-written responses you can reuse!

**Pre-built templates:**
1. "Quick Acknowledgment" - Fast response
2. "Help Needed Response" - Support replies
3. "Feedback Appreciation" - Thank you emails
4. "Meeting Request" - Meeting confirmations
5. "Personal Catch-up" - Friend emails
6. "Newsletter Response" - Newsletter replies
7. "Payment Confirmation" - Payment confirmations

**How to use templates:**

#### Create New Template
1. Click **"+ New Template"** button
2. Fill in:
   - **Name:** "Project Update Response"
   - **Category:** "work"
   - **Body:** "Hi [SENDER_NAME], Thank you for the update..."
3. Click **"Save Template"**
4. Template saved and ready to use

#### Use Variables
Use `[SENDER_NAME]` to insert sender's name automatically:
```
Dear [SENDER_NAME],

Thank you for your message...
```

Gets converted to:
```
Dear John,

Thank you for your message...
```

---

### ⚙️ Feature 6: Settings

**Location:** Click "Settings" in navbar

**What you see:**
- Current Gmail settings
- Ollama configuration
- Classification settings
- Web UI configuration
- System information

**Don't need to change anything here** - it's informational
But you can:
- Change password
- Adjust email check interval (default: 300 seconds = 5 minutes)
- Change Ollama model (if you install new ones)

---

## Step-by-Step Workflow Example

### Complete Email Processing Flow:

#### 👤 Scenario: Customer sends support email

**Step 1: Email arrives**
- Gmail receives email from: support@customer.com
- Subject: "Having trouble with login"

**Step 2: Email Assistant processes it** (automatic)
- Fetches from Gmail
- Classifies as: "support" category
- Scores priority: "high"
- Generates reply using Ollama

**Step 3: You review in Web UI**
- Open http://127.0.0.1:5000
- Click "Drafts"
- See generated reply

**Step 4: Approve or edit**
- If good: Click "✓ Approve"
- If needs changes: Click "✎ Edit" → change text → save

**Step 5: Send from Gmail**
- Go to your Gmail drafts folder
- Open the draft
- Review one more time
- Click "Send"

---

## Step-by-Step: First Time Setup

### Complete Setup (15 minutes)

```
1. Open Terminal 1
   ↓
   ollama serve
   ↓
   ✅ Wait for "Serving on 127.0.0.1:11434"

2. Open Terminal 2
   ↓
   cd C:\Users\awais
   ↓
   pip install -r requirements.txt
   ↓
   ✅ Wait for "Successfully installed"

3. Still in Terminal 2
   ↓
   python web_ui/app.py
   ↓
   ✅ Wait for "Running on http://127.0.0.1:5000"

4. Open Browser
   ↓
   http://127.0.0.1:5000
   ↓
   Login: admin
   ↓
   ✅ Dashboard loads!

5. Test the system
   ↓
   Send yourself test email
   ↓
   Wait 5 minutes
   ↓
   Check "Emails" to see it in database
   ↓
   Check "Drafts" to see AI response
   ↓
   Approve or edit
   ↓
   Check Gmail for draft
```

---

## Troubleshooting

### ❌ Problem: "Connection refused" on http://127.0.0.1:5000

**Solution:**
1. Check if Flask is running in Terminal 2
2. See "Running on 127.0.0.1:5000" message?
3. If not, restart:
   ```bash
   python web_ui/app.py
   ```

---

### ❌ Problem: "Cannot connect to Ollama"

**Solution:**
1. Check Terminal 1 - is `ollama serve` running?
2. You should see: `Serving on 127.0.0.1:11434`
3. If not, start it:
   ```bash
   ollama serve
   ```
4. Wait 10 seconds
5. Refresh Flask web page

---

### ❌ Problem: Dashboard shows "unhealthy" services

**Solution:**
- Check which service is red ✗

**If Gmail ✗:**
- Delete `gmail_token.pickle`
- Run: `python main.py` once
- Will prompt you to authenticate
- Browser opens → Login to Gmail → Click Allow

**If Ollama ✗:**
- Make sure `ollama serve` is running in Terminal 1
- Check no other app using port 11434

**If Database ✗:**
- Usually auto-creates `email_assistant.db`
- Check if file exists: `C:\Users\awais\email_assistant.db`
- If missing, delete and restart Flask

---

### ❌ Problem: No emails showing up

**Solution:**
1. Make sure `python main.py` is running in another terminal
2. Wait 5 minutes (default check interval)
3. Or manually send yourself an email from another account
4. Wait 1-2 minutes
5. Refresh "Emails" page

---

### ❌ Problem: "ModuleNotFoundError: No module named 'flask'"

**Solution:**
```bash
pip install -r requirements.txt
```

If still fails:
```bash
pip install flask flask-cors langdetect
```

---

### ❌ Problem: Draft not showing up in Gmail

**Solution:**
1. Click "✓ Approve" button again
2. Wait 10 seconds
3. Refresh Gmail (F5)
4. Check Drafts folder (not Inbox!)
5. Check if email was already marked as read

---

### ❌ Problem: "Incorrect password"

**Solution:**
- Default password: `admin`
- Make sure Caps Lock is OFF
- Can't remember? Edit `config.json`:
  ```json
  "web_ui": {
      "password": "newpassword"
  }
  ```

---

## Tips & Tricks

### 💡 Tip 1: Keep services running
- Always have `ollama serve` running
- Use Python to start Flask (don't close terminal)
- Use `python main.py` in 3rd terminal for email monitoring

### 💡 Tip 2: Test with your own email
1. Send email to yourself from another email
2. Check Web UI "Emails" page
3. See if it appears (wait 5 min)
4. Check "Drafts" to see generated reply

### 💡 Tip 3: Customize templates
1. Delete generic templates
2. Create templates specific to YOUR emails
3. Add [SENDER_NAME], [EMAIL_DATE] variables
4. Reuse them for similar emails

### 💡 Tip 4: Use analytics
- Check "Analytics" to understand your email patterns
- See which categories have most emails
- Optimize templates based on trends

### 💡 Tip 5: Monitor logs
Terminal where you run `python main.py` shows:
- Which emails are found
- What Ollama generates
- Any errors

Watch logs to debug issues!

---

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Dashboard | Click logo |
| Refresh page | F5 |
| Logout | Click "Logout" |
| Edit draft | Click "✎ Edit" |
| Approve draft | Click "✓ Approve" |
| Delete draft | Click "✕ Delete" |

---

## Next Steps

### 🚀 Advanced Setup (Optional)

1. **Change default password:**
   - Edit `config.json`
   - Change `"password": "admin"` to your password

2. **Install different Ollama model:**
   ```bash
   ollama pull llama2
   ```
   Then change in `config.json`:
   ```json
   "primary_model": "llama2"
   ```

3. **Change email check interval:**
   - Edit `config.json`
   - Change `"check_interval_seconds": 300` to your preference

4. **Enable auto-marking as read:**
   - Edit `config.json`
   - Change `"mark_as_read": false` to `true`

---

## Quick Reference

### Files to Know About

| File | Purpose |
|------|---------|
| `main.py` | Email monitoring service |
| `web_ui/app.py` | Web interface |
| `config.json` | All settings |
| `email_assistant.db` | Database (auto-created) |
| `email_assistant.log` | Logs from email service |

### URLs to Remember

| Feature | URL |
|---------|-----|
| Login | http://127.0.0.1:5000/ |
| Dashboard | http://127.0.0.1:5000/dashboard |
| Emails | http://127.0.0.1:5000/emails |
| Drafts | http://127.0.0.1:5000/drafts |
| Analytics | http://127.0.0.1:5000/analytics |
| Templates | http://127.0.0.1:5000/templates |
| Settings | http://127.0.0.1:5000/settings |

---

## Support & Issues

If something doesn't work:

1. **Check Terminal Output** - Look for red error messages
2. **Check Service Health** - Dashboard shows what's working
3. **Check Logs** - Look at `email_assistant.log`
4. **Restart Services** - Close terminals and start fresh
5. **Check Config** - Make sure `config.json` is valid JSON

Good luck! 🎉
