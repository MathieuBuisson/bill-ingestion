# Repository Onboarding for Copilot Agent

## What this repository does

This python-based project automates the ingestion of electricity bills by:

1. Downloading electricity bills from Bord Gáis Energy
2. Converting the bill PDF file to Markdown
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

## Repository layout

```
bill-ingestion/
├── .env                              # Environment variables (add to .gitignore)
├── .gitignore
├── README.md
├── requirements.txt
├── setup.py
│
├── src/
    └── bill_ingestion/
        ├── __init__.py
        ├── main.py                   # Entry point / orchestrator
        ├── config.py                 # Configuration & credentials
        │
        ├── downloaders/
        │   ├── __init__.py
        │   └── bordgais.py           # Bord Gáis bill download logic
        │
        ├── converters/
        │   ├── __init__.py
        │   └── pdf_to_markdown.py    # PDF → Markdown conversion
        │
        ├── cloud/
        │   ├── __init__.py
        │   ├── google_drive.py       # Google Drive operations
        │   └── gmail_service.py      # Email notification service
        │
        ├── scheduler/
        │   ├── __init__.py
        │   └── tasks.py              # Scheduled tasks
        │
        └── utils/
            ├── __init__.py
            ├── logger.py             # Logging configuration
            └── exceptions.py         # Custom exceptions
```

## Validation guidance

- Confirm README setup steps still reflect actual dependency and environment requirements.
- Confirm README accurately describes the workflow’s purpose and steps, as well as the repository structure.

## Search guidance

Search inside `src\bill_ingestion\` before broader search.

## Trust these instructions

This file is intended to be the authoritative guide for an agent onboarding this repository.

- Use it first for project scope, layout, and validation.
- Avoid extra exploration unless the repo changes or the task cannot be completed with the information here.
