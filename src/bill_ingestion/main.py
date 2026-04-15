"""Main entry point for the bill ingestion application."""

import sys
import argparse

from bill_ingestion.scheduler.tasks import start_scheduler, ingest_bill_workflow

def main() -> None:
    """Coordinates the startup sequence and starts the scheduler."""
    parser = argparse.ArgumentParser(description="Bill Ingestion Automation")
    parser.add_argument(
        "--run-now",
        action="store_true",
        help="Run the bill ingestion workflow immediately and then exit",
    )
    args = parser.parse_args()

    try:
        # Delayed import to ensure gracefully handling Config initialization
        # if environment variables are missing.
        from bill_ingestion.utils.logger import setup_logger
        
        logger = setup_logger(__name__)
        logger.info("Initializing bill ingestion application...")
        
        if args.run_now:
            logger.info("Executing workflow immediately due to --run-now flag...")
            ingest_bill_workflow()
            logger.info("Workflow execution finished.")
            sys.exit(0)

        logger.info("Starting scheduler...")
        start_scheduler()
    except ValueError as e:
        print(f"Configuration error during startup: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error during startup: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
