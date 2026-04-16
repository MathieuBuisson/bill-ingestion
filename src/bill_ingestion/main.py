"""Main entry point for the bill ingestion application."""

import sys

from bill_ingestion.cloud.gmail_service import GmailService
from bill_ingestion.cloud.google_drive import GoogleDriveService
from bill_ingestion.converters.pdf_to_markdown import PDFToMarkdownConverter
from bill_ingestion.downloaders.bordgais import BordgaisDownloader
from bill_ingestion.utils.logger import setup_logger

logger = setup_logger(__name__)


def ingest_bill_workflow() -> None:
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
    downloader = BordgaisDownloader()
    filename, pdf_data = downloader.download_bill()
    logger.info("Downloaded bill successfully: %s", filename)

    # 2. Upload to Google Drive
    drive_service = GoogleDriveService()
    web_view_link = drive_service.upload_file(filename, pdf_data)
    logger.info("Uploaded to Google Drive successfully. Link: %s", web_view_link)

    # 3. Convert to Markdown
    converter = PDFToMarkdownConverter()
    md_path = converter.convert(filename, pdf_data)
    logger.info("Converted to Markdown successfully. Saved at: %s", md_path)

    # 4. Send notification email
    gmail_service = GmailService()
    gmail_service.send_notification(web_view_link, filename)
    logger.info("Notification email sent successfully.")

    logger.info("Bill ingestion workflow completed successfully.")


def main() -> None:
    """Run the bill ingestion workflow and exit."""
    try:
        ingest_bill_workflow()
    except ValueError as e:
        logger.error("Configuration error: %s", e)
        sys.exit(1)
    except Exception as e:
        logger.error("Unexpected error during workflow: %s", e, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
