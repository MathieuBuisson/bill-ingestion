"""Scheduler and main workflow orchestration module."""

import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from bill_ingestion.cloud.gmail_service import GmailService
from bill_ingestion.cloud.google_drive import GoogleDriveService
from bill_ingestion.converters.pdf_to_markdown import PDFToMarkdownConverter
from bill_ingestion.downloaders.bordgais import BordgaisDownloader

logger = logging.getLogger(__name__)


def ingest_bill_workflow() -> None:
    """
    Main orchestration function for ingesting a bill.
    
    Workflow steps:
    1. Downloads bill from Bord Gáis.
    2. Uploads the PDF to Google Drive.
    3. Converts the PDF to Markdown and saves to the knowledge base.
    4. Sends a notification email.
    """
    try:
        logger.info("Starting bill ingestion workflow...")

        # 1. Download bill
        downloader = BordgaisDownloader()
        filename, pdf_data = downloader.download_bill()
        logger.info(f"Downloaded bill successfully: {filename}")

        # 2. Upload to Google Drive
        drive_service = GoogleDriveService()
        web_view_link = drive_service.upload_file(filename, pdf_data)
        logger.info(f"Uploaded to Google Drive successfully. Link: {web_view_link}")

        # 3. Convert to Markdown
        converter = PDFToMarkdownConverter()
        md_path = converter.convert(filename, pdf_data)
        logger.info(f"Converted to Markdown successfully. Saved at: {md_path}")

        # 4. Send Notification Email
        gmail_service = GmailService()
        gmail_service.send_notification(web_view_link, filename)
        logger.info("Notification email sent successfully.")

        logger.info("Bill ingestion workflow completed successfully.")

    except Exception as e:
        logger.error(f"Error during bill ingestion workflow: {e}", exc_info=True)


def start_scheduler() -> None:
    """
    Configures and starts the apscheduler to run the workflow on a schedule.
    Matches the n8n logic: Every 2 months on the 20th at 13:25.
    """
    scheduler = BlockingScheduler()

    trigger = CronTrigger(month="*/2", day=20, hour=13, minute=25)

    scheduler.add_job(ingest_bill_workflow, trigger)
    
    logger.info("Scheduler configured. Waiting for the next scheduled run...")
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped.")
