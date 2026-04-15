"""PDF to Markdown converter module."""

import os
from pathlib import Path

import pymupdf4llm

from bill_ingestion.config import Config


class PDFToMarkdownConverter:
    """Converter for transforming PDF files to Markdown format."""

    def convert(self, filename: str, pdf_data: bytes) -> str:
        """
        Converts PDF binary data to a Markdown file.

        Args:
            filename: The original PDF filename.
            pdf_data: The PDF file content as bytes.

        Returns:
            The local file path where the Markdown file was saved.
        """
        temp_pdf_path = Config.TEMP_DIR / "temp.pdf"

        # Write PDF to temporary file
        with open(temp_pdf_path, "wb") as f:
            f.write(pdf_data)

        try:
            # Convert PDF to Markdown
            markdown_content = pymupdf4llm.to_markdown(str(temp_pdf_path))
        finally:
            # Clean up the temporary PDF file
            if temp_pdf_path.exists():
                os.remove(temp_pdf_path)

        # Prepare the destination path
        md_filename = filename.replace(".pdf", ".md")
        
        if not Config.MARKDOWN_DESTINATION_FOLDER:
            raise ValueError("MARKDOWN_DESTINATION_FOLDER configuration is not set.")
            
        destination_dir = Path(Config.MARKDOWN_DESTINATION_FOLDER)
        destination_dir.mkdir(parents=True, exist_ok=True)

        md_path = destination_dir / md_filename

        # Save Markdown content to the destination folder
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        return str(md_path)
