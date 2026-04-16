"""
Bord Gáis downloader module.
"""

import os
import requests
from datetime import datetime
from typing import Tuple

from playwright.sync_api import sync_playwright
from bill_ingestion.config import Config
from bill_ingestion.utils.logger import setup_logger

logger = setup_logger(__name__)


class BordgaisDownloader:
    """Downloader for Bord Gáis Energy bills."""

    def download_bill(self) -> Tuple[str, bytes]:
        """
        Logs in to Bord Gáis Energy and downloads the latest bill.

        Returns:
            tuple: A tuple containing the (filename, pdf_data) where
                   pdf_data is the bill in bytes.
        """
        current = datetime.now()
        year = current.year
        month = current.strftime('%B')
        filename = f"Electricity Bill {year} {month}.pdf"
        email = Config.BORDGAIS_EMAIL
        password = Config.BORDGAIS_PASSWORD

        if not email or not password:
            raise ValueError(
                "BORDGAIS_EMAIL and BORDGAIS_PASSWORD configuration variables "
                "must be set."
            )

        with sync_playwright() as p:
            # headless=True means no visible browser window — runs silently in background.
            # Change to headless=False if you want to watch what's happening while testing.
            browser = p.chromium.launch(headless=True)
            try:
                context = browser.new_context()
                page = context.new_page()

                # Store the PDF URL once we intercept it
                pdf_url = {"value": None}

                def handle_response(response):
                    # Filter for XHR/Fetch requests to ignore images, CSS, and generic page loads
                    if response.request.resource_type in ["fetch", "xhr"] and response.status == 200:
                        if 'document' in response.url or 'bill' in response.url:
                            try:
                                data = response.json()
                                if isinstance(data, dict) and 'url' in data:
                                    if 'amazonaws' in data['url']:
                                        pdf_url["value"] = data['url']
                                        logger.info("Intercepted PDF URL from background API payload.")
                            except Exception:
                                # Safely ignore responses that aren't valid JSON
                                pass

                # Listen to the entire context, not just the initial page
                context.on('response', handle_response)

                # Step 1: Log in
                page.goto("https://www.bordgaisenergy.ie/login")
                page.fill('input[name="email"]', email)
                page.fill('input[name="password"]', password)
                page.click('button[type="submit"]')
                page.wait_for_url("**/my-accounts**", timeout=15000)

                # Step 2: Go to your specific account page
                page.goto(f"https://www.bordgaisenergy.ie/acc-mgmt/my-accounts/{Config.BORDGAIS_ACCOUNT_ID}/0")
                page.get_by_test_id("navigation-button-group__bills").click()

                # Catch the new tab opening
                with context.expect_page() as new_page_info:
                    page.locator('div.latestBillSummary__download').get_by_test_id('download-button').click()

                new_tab = new_page_info.value

                # Yield to the event loop while waiting for the API to resolve
                logger.info("New tab opened. Waiting for the Next.js app to fetch the S3 URL...")

                max_wait_seconds = 20
                elapsed_seconds = 0

                while pdf_url["value"] is None and elapsed_seconds < max_wait_seconds:
                    # wait_for_timeout allows Playwright to continue processing background network
                    # events (like our API call) while pausing this specific while loop.
                    new_tab.wait_for_timeout(1000)
                    elapsed_seconds += 1

                if not pdf_url["value"]:
                    raise Exception("Timed out waiting for the dynamic API call to return the PDF URL.")

                logger.info(f"Captured S3 URL: {pdf_url['value'][:80]}...")
            finally:
                browser.close()

        # Download the PDF using the requests library
        logger.info("Downloading PDF file from S3 URL ...")
        response = requests.get(pdf_url["value"], timeout=30)
        response.raise_for_status() # Raises an error if the download failed

        with open(filename, 'wb') as f:
            f.write(response.content)

        logger.info(f"Bill saved to {filename}")

        return filename, response.content
