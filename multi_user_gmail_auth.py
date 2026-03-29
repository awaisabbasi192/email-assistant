"""Multi-user Gmail OAuth authentication with per-user token management."""

import os
import json
import logging
import secrets
from typing import Optional, Dict
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from token_encryption import get_encryption

logger = logging.getLogger(__name__)

SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',  # Full Gmail access (compose, send, etc.)
    'https://www.googleapis.com/auth/userinfo.email'  # Get user email
]


class MultiUserGmailAuthenticator:
    """Handles per-user Gmail OAuth with encrypted token storage."""

    def __init__(self, db_manager, redirect_uri: str = "http://localhost:5000/oauth/gmail/callback"):
        """
        Initialize multi-user Gmail authenticator.

        Args:
            db_manager: DatabaseManager instance
            redirect_uri: OAuth redirect URI (must match Google Console settings)
        """
        self.db = db_manager
        self.redirect_uri = redirect_uri
        self.encryption = get_encryption()

        # Load credentials.json (from Google Cloud Console)
        self.credentials_file = "credentials.json"

        if not os.path.exists(self.credentials_file):
            logger.warning(f"credentials.json not found. Please download from Google Cloud Console.")
            raise FileNotFoundError(
                f"Missing {self.credentials_file}\n"
                "Steps to get credentials:\n"
                "1. Go to https://console.cloud.google.com\n"
                "2. Create/select a project\n"
                "3. Enable Gmail API\n"
                "4. Create OAuth 2.0 Credentials (Web application)\n"
                "5. Add redirect URI: " + redirect_uri + "\n"
                "6. Download credentials and save as credentials.json"
            )

    def get_oauth_url(self, user_id: int, state: Optional[str] = None) -> tuple:
        """
        Generate Google OAuth URL for user to authorize.

        Args:
            user_id: User ID (for storing state)
            state: Optional state token (generated if not provided)

        Returns:
            Tuple of (oauth_url, state_token)
        """
        try:
            # Generate state token (CSRF protection)
            if not state:
                state = secrets.token_urlsafe(32)

            # Create OAuth flow
            flow = Flow.from_client_secrets_file(
                self.credentials_file,
                scopes=SCOPES,
                redirect_uri=self.redirect_uri
            )

            # Generate authorization URL
            auth_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                state=state
            )

            logger.info(f"Generated OAuth URL for user {user_id}")
            return auth_url, state

        except Exception as e:
            logger.error(f"Error generating OAuth URL: {e}")
            raise

    def handle_oauth_callback(self, user_id: int, code: str, state: Optional[str] = None) -> bool:
        """
        Handle OAuth callback from Google.

        Args:
            user_id: User ID
            code: Authorization code from Google
            state: State token for CSRF validation

        Returns:
            True if successful
        """
        try:
            # Create OAuth flow
            flow = Flow.from_client_secrets_file(
                self.credentials_file,
                scopes=SCOPES,
                redirect_uri=self.redirect_uri,
                state=state
            )

            # Exchange code for tokens
            flow.fetch_token(code=code)

            credentials = flow.credentials

            # Get user's Gmail email address
            try:
                gmail_service = build('gmail', 'v1', credentials=credentials)
                profile = gmail_service.users().getProfile(userId='me').execute()
                gmail_email = profile.get('emailAddress', '')
            except Exception as e:
                logger.warning(f"Could not fetch Gmail email address: {e}")
                gmail_email = ''

            # Prepare token data for encryption
            token_data = {
                'access_token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes
            }

            # Encrypt and store
            encrypted_token = self.encryption.encrypt(token_data)

            # Store in database
            self.db.store_oauth_token(
                user_id=user_id,
                token_data=encrypted_token,
                expires_at=None,  # Refresh token doesn't expire
                service='gmail'
            )

            # Update user's Gmail status
            self.db.update_user_gmail_status(user_id, True, gmail_email)

            logger.info(f"OAuth token stored for user {user_id} ({gmail_email})")
            return True

        except Exception as e:
            logger.error(f"Error handling OAuth callback: {e}")
            return False

    def get_user_gmail_service(self, user_id: int) -> Optional:
        """
        Get authenticated Gmail service for user.

        Args:
            user_id: User ID

        Returns:
            Authenticated Gmail service or None if failed
        """
        try:
            # Get encrypted token from database
            oauth_record = self.db.get_oauth_token(user_id, 'gmail')

            if not oauth_record:
                logger.warning(f"No OAuth token found for user {user_id}")
                return None

            # Decrypt token
            token_data = self.encryption.decrypt(oauth_record['token_data'])

            if not token_data:
                logger.error(f"Failed to decrypt OAuth token for user {user_id}")
                return None

            # Recreate credentials object
            credentials = Credentials(
                token=token_data.get('access_token'),
                refresh_token=token_data.get('refresh_token'),
                token_uri=token_data.get('token_uri'),
                client_id=token_data.get('client_id'),
                client_secret=token_data.get('client_secret'),
                scopes=token_data.get('scopes')
            )

            # Check if token expired and refresh if needed
            if credentials.expired and credentials.refresh_token:
                logger.debug(f"Refreshing OAuth token for user {user_id}")
                request = Request()
                credentials.refresh(request)

                # Update stored token with new access token
                token_data['access_token'] = credentials.token
                encrypted_token = self.encryption.encrypt(token_data)
                self.db.store_oauth_token(
                    user_id=user_id,
                    token_data=encrypted_token,
                    service='gmail'
                )

            # Build Gmail service
            gmail_service = build('gmail', 'v1', credentials=credentials)
            logger.debug(f"Created Gmail service for user {user_id}")
            return gmail_service

        except Exception as e:
            logger.error(f"Error creating Gmail service for user {user_id}: {e}")
            return None

    def revoke_user_access(self, user_id: int) -> bool:
        """
        Revoke Gmail access for user (deletes stored tokens).

        Args:
            user_id: User ID

        Returns:
            True if successful
        """
        try:
            # Get token to revoke
            oauth_record = self.db.get_oauth_token(user_id, 'gmail')

            if oauth_record:
                token_data = self.encryption.decrypt(oauth_record['token_data'])
                if token_data and token_data.get('access_token'):
                    # Attempt to revoke token with Google
                    try:
                        import requests
                        revoke_url = f"https://oauth2.googleapis.com/revoke?token={token_data['access_token']}"
                        requests.post(revoke_url)
                        logger.info(f"Revoked OAuth token with Google for user {user_id}")
                    except Exception as e:
                        logger.warning(f"Could not revoke token with Google: {e}")

            # Delete from database
            self.db.delete_oauth_token(user_id, 'gmail')

            # Update user status
            self.db.update_user_gmail_status(user_id, False, None)

            logger.info(f"Deleted OAuth token for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error revoking user access: {e}")
            return False

    def is_user_connected(self, user_id: int) -> bool:
        """Check if user has Gmail connected."""
        try:
            oauth_record = self.db.get_oauth_token(user_id, 'gmail')
            return oauth_record is not None
        except Exception as e:
            logger.error(f"Error checking user connection: {e}")
            return False

    def get_user_gmail_email(self, user_id: int) -> Optional[str]:
        """Get connected Gmail email for user."""
        try:
            user = self.db.get_user_by_id(user_id)
            if user and user.get('gmail_connected'):
                return user.get('gmail_email')
            return None
        except Exception as e:
            logger.error(f"Error getting user Gmail email: {e}")
            return None
