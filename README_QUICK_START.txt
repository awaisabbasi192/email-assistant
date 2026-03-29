╔════════════════════════════════════════════════════════════════════════╗
║                   EMAIL ASSISTANT PRO - Quick Start Guide              ║
╚════════════════════════════════════════════════════════════════════════╝

🚀 EASIEST WAY TO START (Just 2 clicks!):

1. FIRST TIME SETUP
   ✅ Download Ollama from: https://ollama.ai
   ✅ Install Ollama
   ✅ Run this command once to get the model:
      ollama pull mistral

2. EVERY TIME YOU WANT TO USE IT

   Step A: Start Ollama (Keep this window open)
   ─────────────────────────────────────────
   Double-click: START_OLLAMA.bat

   Wait for it to say:
   "listening on 127.0.0.1:11434"

   ⚠️  Keep this window OPEN in the background

   Step B: Start Email Assistant (New window)
   ──────────────────────────────────────────
   Double-click: START_EMAIL_ASSISTANT.bat

   It will:
   ✓ Check if Ollama is running
   ✓ Start email processor in background
   ✓ Open web browser automatically
   ✓ Show password for login

3. LOGIN & USE
   ───────────
   • Browser opens automatically to: http://127.0.0.1:5000
   • Login with password: admin
   • View your email assistant dashboard!

═══════════════════════════════════════════════════════════════════════════

📊 DASHBOARD FEATURES:

✓ Dashboard
  - See email stats
  - Processing rate
  - Service health

✓ Emails
  - View all processed emails
  - Filter by category
  - See which are processed

✓ Drafts
  - See AI-generated replies
  - Edit drafts before sending
  - Delete all drafts with one button
  - Approve and send to Gmail

✓ Analytics
  - Charts and statistics
  - Daily processing rates
  - Category distribution

✓ Settings
  - Configuration options

═══════════════════════════════════════════════════════════════════════════

⚙️  HOW IT WORKS:

Background Process:
  • Every 60 seconds, checks for new unread emails
  • Reads email content
  • Generates personalized replies using AI (Ollama)
  • Creates draft in Gmail
  • Marks email as read
  • Saves to database

Web Interface:
  • Review all generated drafts
  • Edit if needed
  • Approve and send
  • Delete drafts
  • View analytics

═══════════════════════════════════════════════════════════════════════════

❓ TROUBLESHOOTING:

Q: "Cannot connect to Ollama"
A: Make sure START_OLLAMA.bat is running in background
   • It should say "listening on 127.0.0.1:11434"

Q: "Gmail credentials not found"
A: App will ask you to authorize first time
   • Follow the Google OAuth login screen
   • Token will be saved automatically

Q: "No emails processing"
A: Check:
   • Ollama is running (START_OLLAMA.bat)
   • Gmail has unread emails
   • Check web UI > Analytics for details

Q: "Script is too slow"
A: It's normal to take 30-60 seconds per email with Ollama
   • This is using free, offline AI
   • Depends on your CPU

Q: "How to stop the app"
A: Just close the browser and email assistant window
   • Ollama window can stay open (or close it too)

═══════════════════════════════════════════════════════════════════════════

📝 COMMAND LINE ALTERNATIVE:

If you prefer terminal:

1. Start Ollama in Terminal 1:
   $ ollama serve

2. Start Email Assistant in Terminal 2:
   $ python app.py

═══════════════════════════════════════════════════════════════════════════

🔧 CONFIGURATION:

To change settings, edit config.json:
  • check_interval_seconds: How often to check emails (default: 60)
  • max_results: Emails to process per check (default: 5)
  • password: Web UI login password (default: admin)
  • port: Web server port (default: 5000)

═══════════════════════════════════════════════════════════════════════════

💡 TIPS:

• Keep both windows open while using
• Drafts are saved locally - no emails sent automatically
• Always review AI replies before approving
• Mark as read happens automatically
• Logs are saved to email_assistant.log

═══════════════════════════════════════════════════════════════════════════

Need help? Check the logs:
  • email_assistant.log (main process)
  • web_ui/web_ui.log (web interface)

═══════════════════════════════════════════════════════════════════════════
