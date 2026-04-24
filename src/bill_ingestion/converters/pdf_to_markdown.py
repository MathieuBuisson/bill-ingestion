"""PDF to Markdown converter module."""

import logging
from pathlib import Path
from typing import cast

import tempfile
import pymupdf4llm

from bill_ingestion.config import Config
from bill_ingestion.utils.exceptions import ConversionError


class PDFToMarkdownConverter:
    """Converter for transforming PDF files to Markdown format."""

    def __init__(self, config: Config):
        self.config = config

        if not self.config.MARKDOWN_DESTINATION_FOLDER:
            raise ConversionError(
                "MARKDOWN_DESTINATION_FOLDER configuration is not set."
            )

    def convert(self, filename: str, pdf_data: bytes) -> str:
        """
        Converts PDF binary data to a Markdown file.

        Args:
            filename: The original PDF filename.
            pdf_data: The PDF file content as bytes.

        Returns:
            The file path where the Markdown file was saved as a string.
        """
        if not pdf_data:
            raise ConversionError("pdf_data cannot be empty")

        # Write PDF to temporary file with cleanup on error
        temp_pdf_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(pdf_data)
                temp_pdf_path = Path(tmp.name)
        except Exception as e:
            raise ConversionError(
                f"Failed to create temporary PDF file: '{filename}'"
            ) from e

        try:
            # Convert PDF to Markdown
            markdown_content = pymupdf4llm.to_markdown(str(temp_pdf_path))
        except Exception as e:
            raise ConversionError(
                f"Failed to convert PDF '{filename}' to Markdown"
            ) from e
        finally:
            # Clean up the temporary PDF file
            if temp_pdf_path and temp_pdf_path.exists():
                try:
                    temp_pdf_path.unlink()
                except OSError:
                    logging.warning(f"Failed to delete temp file: {temp_pdf_path}")

        # Prepare the destination path
        md_filename = Path(filename).with_suffix(".md").name

        destination_dir = Path(cast(str, self.config.MARKDOWN_DESTINATION_FOLDER))
        destination_dir.mkdir(parents=True, exist_ok=True)

        md_path = destination_dir / md_filename

        # Save Markdown content to the destination folder
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        return str(md_path)
