"""Main entry point for the bill ingestion application."""

import logging
import sys

from bill_ingestion.config import Config
from bill_ingestion.cloud.gmail_service import GmailService
from bill_ingestion.cloud.google_drive import GoogleDriveService
from bill_ingestion.converters.pdf_to_markdown import PDFToMarkdownConverter
from bill_ingestion.downloaders.bordgais import BordgaisDownloader
from bill_ingestion.utils.logger import setup_logger

def ingest_bill_workflow(
    downloader: BordgaisDownloader,
    drive_service: GoogleDriveService,
    converter: PDFToMarkdownConverter,
    gmail_service: GmailService,
    logger: logging.Logger,
) -> None:
    """
    Main orchestration function for ingesting a bill.

    Workflow steps:
    1. Downloads bill from Bord Gáis.
    2. Uploads the PDF to Google Drive.
    3. Converts the PDF to Markdown and saves to the knowledge base.
    4. Sends a notification email.
    """
    logger.info("Starting bill ingestion workflow...")

    # 1. Download bill
    logger.info("Downloading bill...")
    try:
        filename, pdf_data = downloader.download_bill()
    except Exception:
        logger.error("Failed to download the bill", exc_info=True)
        raise
    logger.info("Downloaded bill successfully: %s", filename)

    # 2. Upload to Google Drive
    logger.info("Uploading bill to Google Drive...")
    try:
        web_view_link = drive_service.upload_file(filename, pdf_data)
    except Exception:
        logger.error("Failed to upload the bill", exc_info=True)
        raise
    logger.info("Uploaded to Google Drive successfully. Link: %s", web_view_link)

    # 3. Convert to Markdown
    logger.info("Converting bill to Markdown...")
    try:
        md_path = converter.convert(filename, pdf_data)
    except Exception:
        logger.error("Failed to convert the bill", exc_info=True)
        raise
    logger.info("Converted to Markdown successfully. Saved at: %s", md_path)

    # 4. Send notification email
    logger.info("Sending notification email...")
    try:
        gmail_service.send_notification(web_view_link, filename)
    except Exception:
        logger.error("Failed to send notification email", exc_info=True)
        raise
    logger.info("Notification email sent successfully.")

    logger.info("Bill ingestion workflow completed successfully.")


def main() -> None:
    """Application entry point."""

    # 1. Fallback logger (always available)
    logging.basicConfig(level=logging.ERROR)
    logger = logging.getLogger(__name__)

    # 2. Initialize configuration
    try:
        config = Config()
    except ValueError as e:
        logger.error("Configuration error: %s", e)
        sys.exit(1)
    except Exception:
        logger.error("Unexpected error initializing configuration.", exc_info=True)
        sys.exit(1)

    # 3. Replace fallback logger with configured logger
    logger = setup_logger(__name__, config)

    # 4. Instantiate services with dependency injection
    try:
        downloader = BordgaisDownloader(config)
        drive_service = GoogleDriveService(config)
        converter = PDFToMarkdownConverter(config)
        gmail_service = GmailService(config)
    except Exception:
        logger.error("Failed to instantiate services.", exc_info=True)
        sys.exit(1)

    # 5. Run workflow
    try:
        ingest_bill_workflow(
            downloader,
            drive_service,
            converter,
            gmail_service,
            logger,
    )
    except Exception:
        logger.error("Unexpected error during workflow.", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
