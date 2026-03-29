"""
Migrate plain-text passwords to bcrypt hashes in config.json.

This script should be run once to convert the existing plain-text password
in config.json to a bcrypt hash. After running this, the password field
will be replaced with password_hash.
"""

import json
import os
import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from auth_utils import PasswordManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def migrate_passwords():
    """Migrate plain-text passwords to bcrypt hashes."""

    config_file = Path('config.json')

    if not config_file.exists():
        logger.error("config.json not found in current directory")
        return False

    # Load config
    with open(config_file, 'r') as f:
        config = json.load(f)

    # Check if already migrated
    web_ui = config.get('web_ui', {})
    if 'password_hash' in web_ui and 'password' not in web_ui:
        logger.info("Config already migrated to use password_hash")
        return True

    # Get plain text password
    if 'password' not in web_ui:
        logger.error("No password found in web_ui config")
        return False

    plain_password = web_ui['password']

    # Hash password
    try:
        hashed = PasswordManager.hash_password(plain_password)
        logger.info(f"Hashing password for user: {web_ui.get('username', 'admin')}")

        # Update config
        web_ui['password_hash'] = hashed
        del web_ui['password']  # Remove plain text password

        # Ensure secret key is secure
        if 'secret_key' in web_ui and web_ui['secret_key'] in ['email-assistant-secret-key-change-in-production', 'CHANGE_THIS_IN_PRODUCTION_generate_with_secrets_module']:
            secure_key = PasswordManager.generate_secure_key()
            web_ui['secret_key'] = secure_key
            logger.info("Generated new secure secret key")

        # Write back to config
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)

        logger.info("Successfully migrated password to bcrypt hash")
        logger.info(f"Updated config.json - password field replaced with password_hash")
        logger.warning("IMPORTANT: Update your password with: python manage_password.py")

        return True

    except Exception as e:
        logger.error(f"Error migrating password: {e}")
        return False


def main():
    """Main entry point."""
    logger.info("Starting password migration...")

    success = migrate_passwords()

    if success:
        logger.info("Migration completed successfully!")
        sys.exit(0)
    else:
        logger.error("Migration failed!")
        sys.exit(1)


if __name__ == '__main__':
    main()
