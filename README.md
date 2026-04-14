# Electricity Bill Ingestion

Python-based automation for downloading, processing, and organizing electricity bills.

## Overview

This project automates the ingestion of electricity bills by:

1. Downloading electricity bills from Bord Gáis Energy
2. Converting the bill PDF to Markdown
3. Uploading the bill PDF file to Google Drive
4. Copying the Markdown file to a personal knowledge base
5. Sending a notification email with the link and other details

## Architecture

The project follows a modular architecture with clear separation of concerns:

- **Downloaders**: Handle bill retrieval from utility providers
- **Converters**: Transform file formats (PDF → Markdown)
- **Cloud Services**: Manage Google Drive and Gmail operations
- **Scheduler**: Handle recurring task execution
- **Configuration**: Centralized settings and environment management

## Prerequisites

- Python 3.9 or higher
- Google Drive and Gmail accounts with OAuth2 credentials
- Bord Gáis online account credentials

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/MathieuBuisson/bill-ingestion.git
cd bill-ingestion
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
python -m playwright install chromium
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Bord Gáis credentials
BORDGAIS_EMAIL=your-email@example.com
BORDGAIS_PASSWORD=your-password

# Google credentials
GOOGLE_CREDENTIALS_FILE=credentials.json
GOOGLE_DRIVE_FOLDER_ID=your-folder-id
NOTIFICATION_EMAIL=your-email@gmail.com

# Logging
LOG_LEVEL=INFO
```

### 5. Set Up Google OAuth2 Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Google Drive API and Gmail API
4. Create OAuth2 credentials (Desktop application)
5. Download and save as `credentials.json` in the project root

### 6. Run the Workflow

To run the automation workflow manually:

```bash
python -m bill_ingestion.main
```

### 7. Enable Scheduled Execution (Optional)

To run the workflow automatically every 2 months on the 20th at 13:25:

```bash
python -m bill_ingestion.scheduler.tasks
```

## Project Structure

```
bill-ingestion/
├── .env                              # Environment variables (add to .gitignore)
├── .gitignore
├── README.md
├── requirements.txt
├── setup.py
│
├── src/
│   └── bill_ingestion/
│       ├── __init__.py
│       ├── main.py                   # Entry point / orchestrator
│       ├── config.py                 # Configuration & credentials
│       │
│       ├── downloaders/
│       │   ├── __init__.py
│       │   └── bordgais.py           # Bord Gáis bill download logic
│       │
│       ├── converters/
│       │   ├── __init__.py
│       │   └── pdf_to_markdown.py    # PDF → Markdown conversion
│       │
│       ├── cloud/
│       │   ├── __init__.py
│       │   ├── google_drive.py       # Google Drive operations
│       │   └── gmail_service.py      # Email notification service
│       │
│       ├── scheduler/
│       │   ├── __init__.py
│       │   └── tasks.py              # Scheduled tasks
│       │
│       └── utils/
│           ├── __init__.py
│           ├── logger.py             # Logging configuration
│           └── exceptions.py         # Custom exceptions
│
├── tests/
│   ├── __init__.py
│   ├── test_downloaders.py
│   ├── test_converters.py
│   └── test_cloud.py
│
└── docs/
    └── DEVELOPMENT.md                # Development guide
```

## Usage Examples

### Manual Workflow Execution

```python
from bill_ingestion.main import BillIngestionWorkflow
from bill_ingestion.config import Config

config = Config()
workflow = BillIngestionWorkflow(config)
workflow.run()
```

### Scheduled Execution

```python
from bill_ingestion.scheduler.tasks import setup_scheduler

scheduler = setup_scheduler()
# Scheduler runs in background
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `BORDGAIS_EMAIL` | Bord Gáis account email | Yes |
| `BORDGAIS_PASSWORD` | Bord Gáis account password | Yes |
| `GOOGLE_CREDENTIALS_FILE` | Path to Google OAuth2 credentials | Yes |
| `GOOGLE_DRIVE_FOLDER_ID` | Target Google Drive folder ID | Yes |
| `NOTIFICATION_EMAIL` | Email to receive bill notifications | Yes |
| `LOG_LEVEL` | Logging level (INFO, DEBUG, etc.) | No |

## Security Notes

- Never commit `.env` file or `credentials.json` to version control
- Use environment variables for all sensitive data
- Rotate Google OAuth2 tokens regularly
- Consider using a secrets manager for production deployments

## Troubleshooting

### Playwright Browser Issues

If you encounter Playwright installation issues on Windows:

```bash
python -m playwright install --with-deps chromium
```

### Google Authentication Issues

Ensure your Google Cloud project has:
- Google Drive API enabled
- Gmail API enabled
- Correct OAuth2 scopes in credentials

### Bord Gáis Login Issues

The Bord Gáis website may change its structure. If the downloader fails:
1. Review the error logs
2. Inspect the website HTML structure
3. Update selectors in `src/bill_ingestion/downloaders/bordgais.py`

## Contributing

When making changes:
1. Follow PEP 8 style guidelines
2. Add type hints to new functions
3. Update tests for new functionality
4. Update documentation as needed

## License

This project is private and maintained by Mathieu Buisson.
