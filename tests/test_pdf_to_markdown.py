import pytest
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path
from bill_ingestion.converters.pdf_to_markdown import PDFToMarkdownConverter
from bill_ingestion.config import Config
from bill_ingestion.utils.exceptions import ConversionError


@pytest.fixture
def mock_config():
    config = MagicMock(spec=Config)
    config.MARKDOWN_DESTINATION_FOLDER = "/fake/destination"
    return config


def test_converter_init_success(mock_config):
    """Test successful initialization of converter."""
    converter = PDFToMarkdownConverter(mock_config)
    assert converter.config == mock_config


def test_converter_init_missing_folder():
    """Test converter initialization fails if destination folder is missing."""
    config = MagicMock(spec=Config)
    config.MARKDOWN_DESTINATION_FOLDER = None

    with pytest.raises(
        ConversionError, match="MARKDOWN_DESTINATION_FOLDER configuration is not set"
    ):
        PDFToMarkdownConverter(config)


def test_convert_empty_pdf_data(mock_config):
    """Test converter fails if empty byte string is passed."""
    converter = PDFToMarkdownConverter(mock_config)
    with pytest.raises(ConversionError, match="pdf_data cannot be empty"):
        converter.convert("test.pdf", b"")


@patch("bill_ingestion.converters.pdf_to_markdown.pymupdf4llm.to_markdown")
@patch("bill_ingestion.converters.pdf_to_markdown.tempfile.NamedTemporaryFile")
@patch("pathlib.Path.mkdir")
@patch("pathlib.Path.exists", return_value=True)
@patch("pathlib.Path.unlink")
@patch("builtins.open", new_callable=mock_open)
def test_convert_success(
    mock_open_file,
    mock_unlink,
    mock_exists,
    mock_mkdir,
    mock_tempfile,
    mock_to_markdown,
    mock_config,
):
    """Test successful conversion and writing to destination."""
    mock_to_markdown.return_value = "# Markdown Content"

    # Mock temp file context manager
    mock_tmp = MagicMock()
    mock_tmp.name = str(Path("/tmp/fake.pdf"))
    mock_tempfile.return_value.__enter__.return_value = mock_tmp

    converter = PDFToMarkdownConverter(mock_config)
    result = converter.convert("bill_2023.pdf", b"fake pdf data")

    # Check that paths and conversions were handled properly
    assert result.endswith("bill_2023.md")
    assert "/fake/destination" in result.replace("\\", "/")

    mock_tmp.write.assert_called_once_with(b"fake pdf data")
    mock_to_markdown.assert_called_once_with(str(Path("/tmp/fake.pdf")))

    # Check that file was written using builtins.open
    mock_open_file.assert_called_once()
    mock_open_file().write.assert_called_once_with("# Markdown Content")

    # Check temp file cleanup
    mock_unlink.assert_called_once()


@patch("bill_ingestion.converters.pdf_to_markdown.tempfile.NamedTemporaryFile")
def test_convert_temp_file_error(mock_tempfile, mock_config):
    """Test converter handles errors during temp file creation."""
    mock_tempfile.side_effect = IOError("Disk full")

    converter = PDFToMarkdownConverter(mock_config)
    with pytest.raises(ConversionError, match="Failed to create temporary PDF file"):
        converter.convert("test.pdf", b"some data")


@patch("bill_ingestion.converters.pdf_to_markdown.pymupdf4llm.to_markdown")
@patch("bill_ingestion.converters.pdf_to_markdown.tempfile.NamedTemporaryFile")
def test_convert_pymupdf_error(mock_tempfile, mock_to_markdown, mock_config):
    """Test converter handles errors from pymupdf4llm."""
    mock_tmp = MagicMock()
    mock_tmp.name = "/tmp/fake.pdf"
    mock_tempfile.return_value.__enter__.return_value = mock_tmp

    mock_to_markdown.side_effect = Exception("Conversion failed inside library")

    converter = PDFToMarkdownConverter(mock_config)
    with pytest.raises(
        ConversionError, match="Failed to convert PDF 'test.pdf' to Markdown"
    ):
        converter.convert("test.pdf", b"some data")
