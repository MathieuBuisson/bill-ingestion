"""Configuration management for bill ingestion workflow."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration."""

    # Bord Gais credentials
    BORDGAIS_EMAIL = os.getenv("BORDGAIS_EMAIL")
    BORDGAIS_PASSWORD = os.getenv("BORDGAIS_PASSWORD")

    # Google credentials
    GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
    GOOGLE_DRIVE_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
    NOTIFICATION_EMAIL = os.getenv("NOTIFICATION_EMAIL")

    # Paths
    BASE_DIR = Path(__file__).parent.parent.parent
    DATA_DIR = BASE_DIR / "data"
    LOGS_DIR = BASE_DIR / "logs"
    TEMP_DIR = BASE_DIR / "temp"

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    def __init__(self):
        """Initialize configuration and create necessary directories."""
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        self.TEMP_DIR.mkdir(parents=True, exist_ok=True)

        # Validate required configuration
        self._validate_config()

    def _validate_config(self) -> None:
        """Validate that all required configuration is present."""
        required_vars = {
            "BORDGAIS_EMAIL": self.BORDGAIS_EMAIL,
            "BORDGAIS_PASSWORD": self.BORDGAIS_PASSWORD,
            "GOOGLE_CREDENTIALS_FILE": self.GOOGLE_CREDENTIALS_FILE,
            "GOOGLE_DRIVE_FOLDER_ID": self.GOOGLE_DRIVE_FOLDER_ID,
            "NOTIFICATION_EMAIL": self.NOTIFICATION_EMAIL,
        }

        missing = [key for key, value in required_vars.items() if not value]
        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}. \
                Please check your .env file or environment configuration."
            )
