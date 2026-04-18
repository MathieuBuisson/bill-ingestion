"""Google Drive service module."""

import io
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

from bill_ingestion.config import Config
from bill_ingestion.utils.logger import setup_logger

logger = setup_logger(__name__)


class GoogleDriveService:
    """Service for interacting with Google Drive API."""

    SCOPES = ["https://www.googleapis.com/auth/drive"]

    def __init__(self, config: Config):
        """Initialize the Google Drive service."""
        self.config = config
        self.creds = self._get_credentials()
        self.service = build("drive", "v3", credentials=self.creds)

    def _get_credentials(self) -> Credentials:
        """Obtain valid Google Drive API credentials."""
        creds = None
        # Using pathlib for safe path construction
        token_path = self.config.TEMP_DIR / "google_token.json"

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

    def get_or_create_folder(self, name: str, parent_id: str | None = None) -> str:
        """
        Retrieve a folder by name (optionally within a parent),
        or create it if it does not exist.

        Args:
            name: Folder name
            parent_id: Google Drive folder ID of the parent (optional)

        Returns:
            Folder ID (str)
        """
        # Build query
        query = (
            f"name = '{name}' and "
            f"mimeType = 'application/vnd.google-apps.folder' and "
            f"trashed = false"
        )
        if parent_id:
            query += f" and '{parent_id}' in parents"

        # Search for existing folder
        results = (
            self.service.files()
            .list(q=query, fields="files(id, name)", spaces="drive")
            .execute()
        )
        existing = results.get("files", [])

        if existing:
            return existing[0]["id"]

        # Folder not found → create it
        metadata = {
            "name": name,
            "mimeType": "application/vnd.google-apps.folder",
        }
        if parent_id:
            metadata["parents"] = [parent_id]

        folder = self.service.files().create(body=metadata, fields="id").execute()

        logger.info(f"Created folder: {name}")
        return folder["id"]

    def _get_or_create_path(self, path: list[str]) -> str:
        """
        Traverse or create a nested folder hierarchy in Google Drive.
        Each element in ``path`` is treated as a child of the previous one.
        Folders are created on demand if they do not already exist.

        Args:
            path: Ordered list of folder names from root to leaf
                (e.g. ``["Finance", "Taxes", "2026"]``).
                
        Returns:
            The Google Drive folder ID of the deepest (leaf) folder.
        """
        parent_id = None
        for folder in path:
            parent_id = self.get_or_create_folder(folder, parent_id)
        return parent_id

    def _get_or_create_bill_folder(self) -> str:
        """
        Retrieve or create the destination folder for electricity bills.
        Ensures the following fixed folder hierarchy exists in Google Drive,
        creating any missing folders along the way:
        ``Finance / Taxes / <current year> / Income Tax / Electricity Receipts``

        Returns:
            The Google Drive folder ID of the ``Electricity Receipts`` folder.
        """
        year = str(datetime.now().year)

        return self._get_or_create_path([
            "Finance",
            "Taxes",
            year,
            "Income Tax",
            "Electricity Receipts"
        ])

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
            "parents": [self._get_or_create_bill_folder()],
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
