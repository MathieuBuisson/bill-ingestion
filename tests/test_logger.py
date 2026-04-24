import logging
import pytest
from unittest.mock import patch, MagicMock, mock_open
from bill_ingestion.utils.logger import setup_logger
from bill_ingestion.config import Config

@pytest.fixture
def mock_config():
    config = MagicMock(spec=Config)
    config.LOG_LEVEL = "INFO"
    config.LOGS_DIR = MagicMock()
    # Mock the division operator for path concatenation
    config.LOGS_DIR.__truediv__.return_value = "mock_path/bill_ingestion.log"
    return config

@patch('builtins.open', new_callable=mock_open)
def test_setup_logger_success(mock_open_file, mock_config):
    """Test that logger is set up correctly with both stream and file handlers."""
    # Reset logger handlers to isolate test
    logger = logging.getLogger("test_logger_success")
    logger.handlers.clear()
    
    configured_logger = setup_logger("test_logger_success", mock_config)
    
    assert configured_logger.name == "test_logger_success"
    assert configured_logger.level == logging.INFO
    
    # Ensure handlers were added
    assert len(configured_logger.handlers) == 2
    assert any(isinstance(h, logging.StreamHandler) for h in configured_logger.handlers)
    assert any(isinstance(h, logging.FileHandler) for h in configured_logger.handlers)

def test_setup_logger_invalid_level(mock_config):
    """Test that an invalid LOG_LEVEL raises a ValueError."""
    mock_config.LOG_LEVEL = "INVALID_LEVEL"
    
    with pytest.raises(ValueError, match="Invalid LOG_LEVEL 'INVALID_LEVEL'"):
        setup_logger("test_logger_invalid", mock_config)

@patch('builtins.open', new_callable=mock_open)
def test_setup_logger_does_not_duplicate_handlers(mock_open_file, mock_config):
    """Test that handlers are not added multiple times on repeated calls."""
    logger_name = "test_logger_duplicate"
    
    # First setup
    setup_logger(logger_name, mock_config)
    # Second setup
    configured_logger = setup_logger(logger_name, mock_config)
    
    assert len(configured_logger.handlers) == 2
