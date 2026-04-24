import pytest
from bill_ingestion.utils.exceptions import (
    BillIngestionError,
    DownloadError,
    ConversionError,
    GoogleDriveError,
    EmailError,
    ConfigurationError,
)


def test_exception_inheritance():
    """Test that all specific exceptions inherit from the base BillIngestionError."""
    assert issubclass(DownloadError, BillIngestionError)
    assert issubclass(ConversionError, BillIngestionError)
    assert issubclass(GoogleDriveError, BillIngestionError)
    assert issubclass(EmailError, BillIngestionError)
    assert issubclass(ConfigurationError, BillIngestionError)


def test_exception_instantiation():
    """Test that exceptions can be instantiated with a custom message."""
    exc = DownloadError("Test message")
    assert str(exc) == "Test message"
    assert isinstance(exc, Exception)


def test_base_exception():
    """Test the base exception behavior."""
    exc = BillIngestionError("Base error")
    assert str(exc) == "Base error"
    assert isinstance(exc, Exception)
