"""Configuration management for bill ingestion workflow."""

import os
from pathlib import Path
from dotenv import load_dotenv


class Config:
    """Application configuration loaded from environment variables."""

    def __init__(self) -> None:
        # Load environment variables
        load_dotenv()

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
        self.BASE_DIR: Path = Path(__file__).resolve().parents[2]
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
            "GOOGLE_CREDENTIALS_FILE": self.GOOGLE_CREDENTIALS_FILE,
            "NOTIFICATION_EMAIL": self.NOTIFICATION_EMAIL,
            "MARKDOWN_DESTINATION_FOLDER": self.MARKDOWN_DESTINATION_FOLDER,
        }

        missing = [key for key, value in required_vars.items() if not value]
        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}. "
                "Please check your .env file or environment configuration."
            )