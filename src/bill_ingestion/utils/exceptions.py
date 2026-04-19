"""Custom exceptions for bill ingestion workflow."""


class BillIngestionError(Exception):
    """Base exception for bill ingestion errors."""

class DownloadError(BillIngestionError):
    """Raised when bill download fails."""

class ConversionError(BillIngestionError):
    """Raised when PDF to Markdown conversion fails."""

class GoogleDriveError(BillIngestionError):
    """Raised when Google Drive operations fail."""

class EmailError(BillIngestionError):
    """Raised when email sending fails."""

class ConfigurationError(BillIngestionError):
    """Raised when configuration is invalid."""
