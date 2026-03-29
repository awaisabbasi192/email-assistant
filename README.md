# Email Assistant Agent

An intelligent Python-based email assistant that automatically generates contextual draft replies to your unread emails using Claude AI. The agent monitors your Gmail inbox, analyzes incoming emails, and creates thoughtful drafts for your review—all without sending anything automatically.

## Features

- **Automated Email Monitoring**: Continuously checks Gmail for unread emails
- **AI-Powered Replies**: Uses Claude API to generate contextual, appropriate responses
- **Draft Management**: Saves generated replies as Gmail drafts for your review
- **Error Handling**: Comprehensive logging and error recovery
- **Flexible Scheduling**: Run continuously, via cron, or manually
- **Customizable Configuration**: Easy-to-use JSON configuration
- **OAuth 2.0 Authentication**: Secure Gmail access without storing passwords

## Prerequisites

- Python 3.8 or higher
- Gmail account with 2-step verification enabled
- Anthropic API key (get one at https://console.anthropic.com)
- Google Cloud Project with Gmail API enabled

## Setup Instructions

### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown and select "NEW PROJECT"
3. Enter "Email Assistant" as the project name
4. Click "CREATE"
5. Wait for the project to be created

### Step 2: Enable Gmail API

1. In the Google Cloud Console, search for "Gmail API"
2. Click on "Gmail API" in the results
3. Click the "ENABLE" button
4. You'll be redirected to the API page

### Step 3: Create OAuth 2.0 Credentials

1. In the Google Cloud Console, go to **Credentials** (left sidebar)
2. Click **+ CREATE CREDENTIALS** and select **OAuth client ID**
3. You might be prompted to create a consent screen first:
   - Click **Configure Consent Screen**
   - Select **External** as the User Type
   - Click **CREATE**
   - Fill in:
     - App name: "Email Assistant"
     - User support email: Your Gmail address
     - Developer contact: Your Gmail address
   - Click **SAVE AND CONTINUE** through the remaining pages
4. Back to creating OAuth credentials:
   - Select **Desktop application** as the Application type
   - Name it "Email Assistant"
   - Click **CREATE**
5. Click the download button (arrow icon) next to your created credential
6. Save the JSON file as `credentials.json` in your project directory

### Step 4: Set Up Python Environment

1. Clone or download this project
2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - **macOS/Linux**: `source venv/bin/activate`
   - **Windows**: `venv\Scripts\activate`

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Step 5: Configure API Keys

1. Get your Anthropic API key from https://console.anthropic.com
2. Set it as an environment variable:
   - **macOS/Linux**: `export ANTHROPIC_API_KEY='your-key-here'`
   - **Windows PowerShell**: `$env:ANTHROPIC_API_KEY='your-key-here'`
   - **Windows Command Prompt**: `set ANTHROPIC_API_KEY=your-key-here`

Alternatively, the Anthropic SDK will look for this in a `.env` file in your project directory.

### Step 6: Customize Configuration (Optional)

Edit `config.json` to customize behavior:

```json
{
  "gmail": {
    "check_interval_seconds": 300,
    "max_results": 10,
    "mark_as_read": false
  },
  "claude": {
    "temperature": 0.7,
    "max_tokens": 500
  },
  "draft_options": {
    "add_signature": true
  }
}
```

## Running the Agent

### First Run (Authentication)

The first time you run the agent, it will open a browser window to authenticate with Gmail:

```bash
python main.py
```

1. A browser window will open with a Google login screen
2. Log in with your Gmail account
3. Click "Allow" when asked to grant permissions
4. The token will be saved locally for future runs

### Continuous Mode (Default)

Runs the agent continuously, checking for emails at the specified interval:

```bash
python main.py
```

The agent will:
- Check for unread emails every 5 minutes (configurable)
- Generate replies using Claude for each email
- Create Gmail drafts with the generated replies
- Log all activity to `email_assistant.log`
- Continue running until you press `Ctrl+C`

### Single Run Mode

Process emails once and exit (useful for cron jobs):

```bash
python main.py --once
```

## Scheduling with Cron (Linux/macOS)

Edit your crontab:

```bash
crontab -e
```

Add a line to run the agent every 15 minutes:

```cron
*/15 * * * * cd /path/to/email-assistant && /path/to/venv/bin/python main.py --once
```

## Scheduling with Windows Task Scheduler

1. Open Task Scheduler
2. Click "Create Basic Task..."
3. Name: "Email Assistant"
4. Trigger: Set to desired frequency (e.g., every 15 minutes)
5. Action:
   - Program: `C:\path\to\venv\Scripts\python.exe`
   - Arguments: `C:\path\to\main.py --once`
   - Start in: `C:\path\to\project`
6. Click "Finish"

## Configuration Reference

### gmail
- `credentials_file`: Path to OAuth 2.0 credentials JSON
- `token_file`: Where to store the auth token
- `check_interval_seconds`: Seconds between email checks
- `max_results`: Max emails to process per check
- `mark_as_read`: Auto-mark processed emails as read
- `exclude_labels`: Labels to exclude (e.g., DRAFT, SENT)

### claude
- `model`: Claude model to use
- `temperature`: Response creativity (0-1)
- `max_tokens`: Max length of generated replies

### draft_options
- `auto_save_drafts`: Save generated replies as drafts
- `add_signature`: Append signature to drafts
- `signature_text`: Custom signature text

### logging
- `level`: Log level (DEBUG, INFO, WARNING, ERROR)
- `log_file`: Where to save logs
- `console_output`: Also log to console

### features
- `create_labels_for_drafts`: Add label to processed emails
- `draft_label_name`: Name of the label to use

## Understanding the Logs

The agent creates detailed logs in `email_assistant.log`. Check this log if emails aren't being detected or Claude API errors occur.

## Troubleshooting

### "credentials.json not found"
- Download OAuth 2.0 credentials from Google Cloud Console
- Place it in the same directory as `main.py`

### "Failed to authenticate"
- Delete `gmail_token.pickle` and run again
- Ensure Gmail API is enabled in Google Cloud Console

### "ANTHROPIC_API_KEY not found"
- Set the environment variable correctly
- Or create a `.env` file with `ANTHROPIC_API_KEY=your-key`

### No emails being processed
- Verify emails are unread
- Check they're not in excluded labels
- Increase `max_results` in config.json
- Check `email_assistant.log` for errors

## Privacy & Security

- **OAuth Tokens**: Stored locally in `gmail_token.pickle`. Keep it secure.
- **API Keys**: Never commit to version control
- **Email Content**: Sent to Claude API for analysis
- **No Auto-Sending**: Drafts are saved for your review only
- **Never commit**: `credentials.json` or `.env` files

## Architecture

```
main.py                    # Main orchestrator
├── gmail_auth.py          # Gmail API authentication
├── email_processor.py     # Email operations
├── claude_integration.py  # Reply generation
└── config.json            # Configuration
```

## License

This project is provided as-is for personal use.