"""Encryption/decryption utilities for OAuth tokens."""

import os
import json
import logging
from typing import Dict, Optional
from cryptography.fernet import Fernet, InvalidToken

logger = logging.getLogger(__name__)


class TokenEncryption:
    """Encrypt and decrypt OAuth tokens using Fernet (symmetric encryption)."""

    def __init__(self):
        """Initialize encryption manager."""
        self.fernet = self._get_or_create_cipher()

    @staticmethod
    def _get_or_create_cipher() -> Fernet:
        """
        Get or create encryption cipher.

        Encryption key is stored in GMAIL_TOKEN_ENCRYPTION_KEY environment variable.
        If not set, generates and prompts user to set it.
        """
        env_key = os.environ.get('GMAIL_TOKEN_ENCRYPTION_KEY')

        if env_key:
            try:
                return Fernet(env_key.encode())
            except Exception as e:
                logger.error(f"Invalid encryption key in environment: {e}")
                raise

        # Generate new key
        logger.warning("GMAIL_TOKEN_ENCRYPTION_KEY not set, generating new key")
        key = Fernet.generate_key()
        env_file = ".env"

        # Try to write to .env file
        try:
            if os.path.exists(env_file):
                # Append to existing .env
                with open(env_file, 'a') as f:
                    f.write(f"\nGMAIL_TOKEN_ENCRYPTION_KEY={key.decode('utf-8')}\n")
            else:
                # Create new .env
                with open(env_file, 'w') as f:
                    f.write("# Email Assistant Configuration\n")
                    f.write(f"GMAIL_TOKEN_ENCRYPTION_KEY={key.decode('utf-8')}\n")

            logger.info(f"Encryption key saved to {env_file}")
            print(f"✓ Generated encryption key and saved to {env_file}")

        except Exception as e:
            logger.warning(f"Could not write to {env_file}: {e}")
            print(f"⚠ Could not write to {env_file}")
            print(f"Set environment variable: GMAIL_TOKEN_ENCRYPTION_KEY={key.decode('utf-8')}")

        os.environ['GMAIL_TOKEN_ENCRYPTION_KEY'] = key.decode('utf-8')
        return Fernet(key)

    def encrypt(self, token_data: Dict) -> str:
        """
        Encrypt token dictionary to encrypted string.

        Args:
            token_data: Dictionary with token data (access_token, refresh_token, etc.)

        Returns:
            Encrypted string (safe to store in database)
        """
        try:
            # Convert dict to JSON
            json_data = json.dumps(token_data)

            # Encrypt
            encrypted = self.fernet.encrypt(json_data.encode())

            # Return as string
            return encrypted.decode()

        except Exception as e:
            logger.error(f"Error encrypting token: {e}")
            raise

    def decrypt(self, encrypted_data: str) -> Optional[Dict]:
        """
        Decrypt encrypted string back to token dictionary.

        Args:
            encrypted_data: Encrypted string from database

        Returns:
            Decrypted token dictionary or None if failed
        """
        try:
            # Decrypt
            decrypted = self.fernet.decrypt(encrypted_data.encode())

            # Parse JSON
            token_data = json.loads(decrypted.decode())

            return token_data

        except InvalidToken:
            logger.error("Invalid token - encryption key may be wrong")
            return None
        except Exception as e:
            logger.error(f"Error decrypting token: {e}")
            return None


# Global encryption instance
_encryption = None


def get_encryption() -> TokenEncryption:
    """Get or create global encryption instance."""
    global _encryption
    if _encryption is None:
        _encryption = TokenEncryption()
    return _encryption
