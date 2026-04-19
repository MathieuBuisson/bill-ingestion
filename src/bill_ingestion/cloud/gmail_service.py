"""Gmail service module."""

import base64
from email.message import EmailMessage

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from bill_ingestion.config import Config
from bill_ingestion.utils.exceptions import EmailError


class GmailService:
    """Service for interacting with Gmail API."""

    SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

    def __init__(self, config: Config):
        """Initialize the Gmail service."""
        self.config = config
        self.creds = self._get_credentials()
        self.service = build("gmail", "v1", credentials=self.creds)

    def _get_credentials(self) -> Credentials:
        """Obtain valid Gmail API credentials."""
        creds = None
        # Using pathlib to build the path safely
        token_path = self.config.TEMP_DIR / "gmail_token.json"

        if token_path.exists():
            creds = Credentials.from_authorized_user_file(str(token_path), self.SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.config.GOOGLE_CREDENTIALS_FILE, self.SCOPES
                )
                creds = flow.run_local_server(port=0)

            with open(token_path, "w") as token:
                token.write(creds.to_json())

        return creds

    def send_notification(self, web_view_link: str, filename: str) -> None:
        """
        Sends an email notification representing successful ingestion.

        Args:
            web_view_link: Google Drive link for the uploaded file.
            filename: The original filename or local path.
        """
        message = EmailMessage()

        content = (
            "The electricity bill has been uploaded to Google Drive.\n\n"
            f"Link: {web_view_link}\n\n"
            f"Local path: {filename}"
        )

        message.set_content(content)
        message["To"] = self.config.NOTIFICATION_EMAIL
        message["From"] = "me"
        message["Subject"] = "Electricity Bill Ingested"

        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {"raw": encoded_message}

        try:
            self.service.users().messages().send(userId="me", body=create_message).execute()
        except Exception as e:
            raise EmailError(f"Failed to send email notification to {self.config.NOTIFICATION_EMAIL}") from e
