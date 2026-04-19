"""Configuration management for bill ingestion workflow."""

import os
from pathlib import Path
from dotenv import load_dotenv

from bill_ingestion.utils.exceptions import ConfigurationError


class Config:
    """Application configuration loaded from environment variables."""

    def __init__(self) -> None:
        self.BASE_DIR: Path = Path(__file__).resolve().parents[2]

        # Load environment variables
        load_dotenv(self.BASE_DIR / ".env")

        # Bord Gais credentials
        self.BORDGAIS_EMAIL: str | None = os.getenv("BORDGAIS_EMAIL")
        self.BORDGAIS_PASSWORD: str | None = os.getenv("BORDGAIS_PASSWORD")
        self.BORDGAIS_ACCOUNT_ID: str | None = os.getenv("BORDGAIS_ACCOUNT_ID")

        # Google credentials
        self.GOOGLE_CREDENTIALS_FILE: str = os.getenv(
            "GOOGLE_CREDENTIALS_FILE", "credentials.json"
        )
        self.NOTIFICATION_EMAIL: str | None = os.getenv("NOTIFICATION_EMAIL")

        # Paths
        self.DATA_DIR: Path = self.BASE_DIR / "data"
        self.LOGS_DIR: Path = self.BASE_DIR / "logs"
        self.TEMP_DIR: Path = self.BASE_DIR / "temp"
        self.MARKDOWN_DESTINATION_FOLDER: str | None = os.getenv(
            "MARKDOWN_DESTINATION_FOLDER"
        )

        # Logging
        self.LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

        # Initialize directories
        self._create_directories()

        # Validate configuration
        self._validate_config()

    def _create_directories(self) -> None:
        """Ensure required directories exist."""
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        self.TEMP_DIR.mkdir(parents=True, exist_ok=True)

    def _validate_config(self) -> None:
        """Validate that all required configuration is present."""
        required_vars = {
            "BORDGAIS_EMAIL": self.BORDGAIS_EMAIL,
            "BORDGAIS_PASSWORD": self.BORDGAIS_PASSWORD,
            "BORDGAIS_ACCOUNT_ID": self.BORDGAIS_ACCOUNT_ID,
            "NOTIFICATION_EMAIL": self.NOTIFICATION_EMAIL,
            "MARKDOWN_DESTINATION_FOLDER": self.MARKDOWN_DESTINATION_FOLDER,
        }

        missing = [key for key, value in required_vars.items() if not value or not value.strip()]
        if missing:
            raise ConfigurationError(
                f"Missing required environment variables: {', '.join(missing)}. "
                "Please check your .env file or environment configuration."
            )

        # Validate the credentials file actually exists on disk
        credentials_path = Path(self.GOOGLE_CREDENTIALS_FILE)
        if not credentials_path.is_absolute():
            credentials_path = self.BASE_DIR / credentials_path
        if not credentials_path.is_file():
            raise ConfigurationError(
                f"GOOGLE_CREDENTIALS_FILE not found: '{credentials_path}'. "
                "Ensure the file exists or set the correct path in your .env file."
            )

    def __repr__(self) -> str:
        def mask(value: str | None, visible: int = 4) -> str:
            if not value:
                return "None"
            if len(value) <= visible:
                return "***"
            return f"{value[:visible]}***"

        return (
            f"Config("
            f"bordgais_email={mask(self.BORDGAIS_EMAIL)!r}, "
            f"bordgais_password=***REDACTED***, "
            f"bordgais_account_id={mask(self.BORDGAIS_ACCOUNT_ID)!r}, "
            f"notification_email={mask(self.NOTIFICATION_EMAIL)!r}, "
            f"google_credentials_file={self.GOOGLE_CREDENTIALS_FILE!r}, "
            f"markdown_destination_folder={self.MARKDOWN_DESTINATION_FOLDER!r}, "
            f"log_level={self.LOG_LEVEL!r}, "
            f"base_dir={str(self.BASE_DIR)!r}"
            f")"
        )
