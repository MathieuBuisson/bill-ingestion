import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from bill_ingestion.config import Config
from bill_ingestion.utils.exceptions import ConfigurationError


@pytest.fixture
def mock_env():
    return {
        "BORDGAIS_EMAIL": "test@example.com",
        "BORDGAIS_PASSWORD": "password123",
        "BORDGAIS_ACCOUNT_ID": "12345678",
        "NOTIFICATION_EMAIL": "notify@example.com",
        "MARKDOWN_DESTINATION_FOLDER": "/tmp/markdown",
        "GOOGLE_CREDENTIALS_FILE": "test_credentials.json",
        "LOG_LEVEL": "DEBUG",
    }


@patch("bill_ingestion.config.load_dotenv")
@patch("bill_ingestion.config.os.getenv")
@patch("pathlib.Path.mkdir")
@patch("pathlib.Path.is_file", return_value=True)
def test_config_success(
    mock_is_file, mock_mkdir, mock_getenv, mock_load_dotenv, mock_env
):
    """Test that Config successfully initializes when all required variables are present."""
    mock_getenv.side_effect = lambda k, d=None: mock_env.get(k, d)

    config = Config()

    assert config.BORDGAIS_EMAIL == "test@example.com"
    assert config.BORDGAIS_PASSWORD == "password123"
    assert config.LOG_LEVEL == "DEBUG"
    # Ensure directories were attempted to be created
    assert mock_mkdir.call_count == 3


@patch("bill_ingestion.config.load_dotenv")
@patch("bill_ingestion.config.os.getenv")
@patch("pathlib.Path.mkdir")
@patch("pathlib.Path.is_file", return_value=True)
def test_config_missing_required_var(
    mock_is_file, mock_mkdir, mock_getenv, mock_load_dotenv, mock_env
):
    """Test that Config raises ConfigurationError when a required variable is missing."""
    mock_env["BORDGAIS_EMAIL"] = ""
    mock_getenv.side_effect = lambda k, d=None: mock_env.get(k, d)

    with pytest.raises(
        ConfigurationError,
        match="Missing required environment variables: BORDGAIS_EMAIL",
    ):
        Config()


@patch("bill_ingestion.config.load_dotenv")
@patch("bill_ingestion.config.os.getenv")
@patch("pathlib.Path.mkdir")
@patch("pathlib.Path.is_file", return_value=False)
def test_config_missing_credentials_file(
    mock_is_file, mock_mkdir, mock_getenv, mock_load_dotenv, mock_env
):
    """Test that Config raises ConfigurationError when credentials file doesn't exist."""
    mock_getenv.side_effect = lambda k, d=None: mock_env.get(k, d)

    with pytest.raises(ConfigurationError, match="GOOGLE_CREDENTIALS_FILE not found"):
        Config()


@patch("bill_ingestion.config.load_dotenv")
@patch("bill_ingestion.config.os.getenv")
@patch("pathlib.Path.mkdir")
@patch("pathlib.Path.is_file", return_value=True)
def test_config_repr(mock_is_file, mock_mkdir, mock_getenv, mock_load_dotenv, mock_env):
    """Test the __repr__ method properly masks sensitive values."""
    mock_getenv.side_effect = lambda k, d=None: mock_env.get(k, d)

    config = Config()
    repr_str = repr(config)

    assert "bordgais_password=***REDACTED***" in repr_str
    assert "test***" in repr_str  # Masked email
    assert "1234***" in repr_str  # Masked account ID
