"""Gmail API authentication and client management."""

import pickle
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.api_core import retry
import logging

logger = logging.getLogger(__name__)

# Gmail API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify'
]


class GmailAuthenticator:
    """Handles Gmail API authentication and token management."""

    def __init__(self, credentials_file: str, token_file: str):
        """
        Initialize Gmail authenticator.

        Args:
            credentials_file: Path to OAuth 2.0 credentials JSON file
            token_file: Path to store OAuth 2.0 token (pickle)
        """
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.creds = None

    def authenticate(self) -> Credentials:
        """
        Authenticate with Gmail API using OAuth 2.0.

        Returns:
            Authenticated credentials object
        """
        # Load existing token if available
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                self.creds = pickle.load(token)
                logger.info("Loaded existing OAuth token from file")

        # Refresh token if expired
        if self.creds and self.creds.expired and self.creds.refresh_token:
            try:
                self.creds.refresh(Request())
                logger.info("Refreshed expired OAuth token")
            except Exception as e:
                logger.warning(f"Failed to refresh token: {e}. Will re-authenticate.")
                self.creds = None

        # If no valid credentials, perform new authentication
        if not self.creds or not self.creds.valid:
            if not os.path.exists(self.credentials_file):
                raise FileNotFoundError(
                    f"Credentials file not found: {self.credentials_file}\n"
                    "Please follow the setup instructions in README.md"
                )

            flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_file,
                SCOPES
            )
            self.creds = flow.run_local_server(port=0)
            logger.info("Performed new OAuth 2.0 authentication")

            # Save token for future use
            with open(self.token_file, 'wb') as token:
                pickle.dump(self.creds, token)
                logger.info(f"Saved OAuth token to {self.token_file}")

        return self.creds

    def get_service(self):
        """
        Get authenticated Gmail API service.

        Returns:
            Gmail API service object
        """
        from google.oauth2 import service_account
        from googleapiclient.discovery import build

        if not self.creds:
            self.authenticate()

        service = build('gmail', 'v1', credentials=self.creds)
        logger.info("Created Gmail API service")
        return service
