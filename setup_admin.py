#!/usr/bin/env python3
"""
Setup script to create admin user and initialize database.
Run this once before deploying to Render.
"""

import sys
import os
import sqlite3
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import DatabaseManager
from auth_utils import PasswordManager

def setup_admin_user():
    """Create admin user in database."""
    try:
        # Initialize database
        db = DatabaseManager("email_assistant.db")

        # Admin credentials
        admin_username = "awais"
        admin_email = "admin@emailassistant.local"
        admin_password = "admin"

        # Hash password
        password_manager = PasswordManager()
        password_hash = password_manager.hash_password(admin_password)

        # Connect to database
        conn = db.get_connection()
        cursor = conn.cursor()

        try:
            # Check if admin user already exists
            cursor.execute("SELECT id FROM users WHERE username = ?", (admin_username,))
            existing_user = cursor.fetchone()

            if existing_user:
                print("[OK] Admin user '{}' already exists".format(admin_username))
                conn.close()
                return

            # Create admin user
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, is_active, gmail_connected)
                VALUES (?, ?, ?, ?, ?)
            """, (admin_username, admin_email, password_hash, 1, 0))

            conn.commit()

            print("[OK] Admin user created successfully!")
            print("   Username: {}".format(admin_username))
            print("   Password: {}".format(admin_password))
            print("   Email: {}".format(admin_email))
            print("\n[WARNING] IMPORTANT: Change this password after first login!")

        except sqlite3.IntegrityError as e:
            print("[ERROR] Error creating admin user: {}".format(e))
            print("User might already exist")
        finally:
            conn.close()

    except Exception as e:
        print("[ERROR] Setup failed: {}".format(e))
        sys.exit(1)

if __name__ == "__main__":
    print("Email Assistant - Admin Setup")
    print("=" * 40)
    setup_admin_user()
    print("\n[OK] Setup complete! You can now login with:")
    print("   Username: awais")
    print("   Password: admin")
