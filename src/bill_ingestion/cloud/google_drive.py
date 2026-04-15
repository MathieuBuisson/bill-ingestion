"""Google Drive service module."""

import io
import os
from typing import Dict, Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

from bill_ingestion.config import Config


class GoogleDriveService:
    """Service for interacting with Google Drive API."""

    SCOPES = ["https://www.googleapis.com/auth/drive.file"]

    def __init__(self):
        """Initialize the Google Drive service."""
        self.creds = self._get_credentials()
        self.service = build("drive", "v3", credentials=self.creds)

    def _get_credentials(self) -> Credentials:
        """Obtain valid Google Drive API credentials."""
        creds = None
        # Using pathlib for safe path construction
        token_path = Config.TEMP_DIR / "drive_token.json"

        if token_path.exists():
            creds = Credentials.from_authorized_user_file(str(token_path), self.SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    Config.GOOGLE_CREDENTIALS_FILE, self.SCOPES
                )
                creds = flow.run_local_server(port=0)

            with open(token_path, "w") as token:
                token.write(creds.to_json())

        return creds

    def upload_file(self, filename: str, binary_data: bytes) -> str:
        """
        Uploads a file to Google Drive.

        Args:
            filename: The name of the file to save as.
            binary_data: The file content as bytes.

        Returns:
            The webViewLink of the uploaded file.
        """
        file_metadata = {
            "name": filename,
            "parents": [Config.GOOGLE_DRIVE_FOLDER_ID],
        }

        media = MediaIoBaseUpload(
            io.BytesIO(binary_data), mimetype="application/pdf", resumable=True
        )

        file = (
            self.service.files()
            .create(body=file_metadata, media_body=media, fields="id, webViewLink")
            .execute()
        )

        # Retrieve the generated webViewLink to share
        return file.get("webViewLink", "")
