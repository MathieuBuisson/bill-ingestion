"""Custom exceptions for bill ingestion workflow."""


class BillIngestionError(Exception):
    """Base exception for bill ingestion errors."""

    pass


class DownloadError(BillIngestionError):
    """Raised when bill download fails."""

    pass


class ConversionError(BillIngestionError):
    """Raised when PDF to Markdown conversion fails."""

    pass


class GoogleDriveError(BillIngestionError):
    """Raised when Google Drive operations fail."""

    pass


class EmailError(BillIngestionError):
    """Raised when email sending fails."""

    pass


class ConfigurationError(BillIngestionError):
    """Raised when configuration is invalid."""

    pass