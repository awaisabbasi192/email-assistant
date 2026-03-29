#!/usr/bin/env python3
"""
Email Assistant - Unified Application Launcher
Starts both email processor and web UI in a single interface
"""

import os
import sys
import json
import logging
import threading
import time
import webbrowser
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_ollama():
    """Check if Ollama is running."""
    try:
        import requests
        response = requests.get("http://127.0.0.1:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            if models:
                logger.info("✅ Ollama is running")
                return True
            else:
                logger.error("❌ Ollama has no models. Run: ollama pull mistral")
                return False
        else:
            logger.error("❌ Ollama server not responding")
            return False
    except Exception as e:
        logger.error(f"❌ Cannot connect to Ollama: {e}")
        logger.error("   Make sure to run: ollama serve")
        return False


def start_email_processor():
    """Start email processor in background thread."""
    try:
        logger.info("\n" + "="*60)
        logger.info("Starting Email Processor...")
        logger.info("="*60)

        import json
        from pathlib import Path
        from auto_processor import SimpleEmailProcessor

        # Load config
        config_file = Path('config.json')
        with open(config_file) as f:
            config = json.load(f)

        # Create and run processor
        processor = SimpleEmailProcessor(config)

        # Run in background
        logger.info("✅ Email processor started successfully")
        logger.info(f"📧 Will check emails every {config['gmail']['check_interval_seconds']} seconds")
        logger.info(f"   Processing {min(3, config['gmail']['max_results'])} emails per check")
        logger.info(f"✓ Emails will be classified automatically")
        logger.info(f"✓ Draft replies will be generated and saved\n")

        processor.run()

    except KeyboardInterrupt:
        logger.info("Email processor stopped by user")
    except Exception as e:
        logger.error(f"❌ Error in email processor: {e}")
        logger.error("   Check email_assistant.log for details")


def start_web_ui():
    """Start web UI in main thread."""
    try:
        logger.info("\n" + "="*60)
        logger.info("Starting Web Interface...")
        logger.info("="*60)

        # Import Flask app
        from web_ui.app import app, CONFIG

        host = CONFIG.get('web_ui', {}).get('host', '127.0.0.1')
        port = CONFIG.get('web_ui', {}).get('port', 5000)
        url = f"http://{host}:{port}"

        logger.info(f"✅ Web UI starting at {url}")
        logger.info(f"   Password: {CONFIG.get('web_ui', {}).get('password', 'admin')}")
        logger.info(f"\n🌐 Opening browser in 3 seconds...\n")

        # Open browser after a short delay
        threading.Timer(3.0, lambda: webbrowser.open(url)).start()

        # Run Flask
        app.run(host=host, port=port, debug=False, use_reloader=False)

    except Exception as e:
        logger.error(f"❌ Error in web UI: {e}")


def main():
    """Main application launcher."""
    logger.info("\n" + "="*60)
    logger.info("EMAIL ASSISTANT - UNIFIED APPLICATION")
    logger.info("="*60 + "\n")

    # Step 1: Check Ollama
    logger.info("Step 1: Checking dependencies...\n")
    if not check_ollama():
        logger.error("\n❌ Cannot start: Ollama is not running")
        logger.error("   Please run in another terminal:")
        logger.error("   $ ollama serve\n")
        sys.exit(1)

    # Step 2: Start email processor in background thread
    logger.info("\nStep 2: Starting services...\n")

    # Start email processor in daemon thread
    processor_thread = threading.Thread(target=start_email_processor, daemon=True)
    processor_thread.start()

    # Give processor time to start
    time.sleep(2)

    # Step 3: Start web UI in main thread
    logger.info("\nStep 3: Starting web interface...\n")
    try:
        start_web_ui()
    except KeyboardInterrupt:
        logger.info("\n\n✅ Application shutting down gracefully...")
        logger.info("   Email processor will stop")
        sys.exit(0)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n✅ Application stopped")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
