import requests
import schedule
import time
import os
from threading import Thread

# Aapka deployed app ka URL (Render deploy karne ke baad milega)
RENDER_URL = os.getenv("RENDER_URL", "http://localhost:5000")

def keep_alive():
    """Render app ko active rakhne ke liye ping karo"""
    try:
        response = requests.get(RENDER_URL)
        print(f"✅ Keep-alive ping sent - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Keep-alive failed: {e}")

def schedule_keepalive():
    """Har 10 minutes mein ping karo"""
    schedule.every(10).minutes.do(keep_alive)

    while True:
        schedule.run_pending()
        time.sleep(60)

def start_keep_alive():
    """Background thread mein keep-alive start karo"""
    thread = Thread(target=schedule_keepalive, daemon=True)
    thread.start()
    print("🔄 Keep-alive script started (runs every 10 minutes)")

if __name__ == "__main__":
    print("Starting keep-alive service...")
    schedule_keepalive()
