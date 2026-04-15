"""
Bord Gáis downloader module.
"""

import os
from datetime import datetime
from typing import Tuple

from playwright.sync_api import sync_playwright


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

        email = os.getenv("BORDGAS_EMAIL")
        password = os.getenv("BORDGAS_PASSWORD")

        if not email or not password:
            raise EnvironmentError(
                "BORDGAS_EMAIL and BORDGAS_PASSWORD environment variables "
                "must be set."
            )

        with sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                page = browser.new_page()
                page.goto("https://www.bordgaisenergy.ie/login")
                page.fill('input[name="email"]', email)
                page.fill('input[name="password"]', password)
                page.click('button[type="submit"]')
                page.wait_for_load_state("networkidle")

                # TODO: Navigate to bills page and download the PDF
                # This is placeholder code - adjust based on actual website
                # For example:
                # page.click('a[href*="bill"]')
                # download = page.wait_for_download()
                # download.save_as(filename)
                # with open(filename, 'rb') as f:
                #     pdf_data = f.read()
                # os.remove(filename)

                # Placeholder
                pdf_data = b"dummy pdf data"
            finally:
                browser.close()

        return filename, pdf_data
