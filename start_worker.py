"""Start the background task worker for processing document generation tasks."""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from src.task_worker import TaskWorker
from loguru import logger


async def main():
    """Main entry point for the task worker."""
    logger.info("=" * 60)
    logger.info("Task Worker Starting")
    logger.info("=" * 60)
    logger.info("")
    logger.info("")
    logger.info("Ctrl+C")
    logger.info("")
    logger.info("=" * 60)

    worker = TaskWorker()

    try:
        await worker.run_forever(interval=5)
    except KeyboardInterrupt:
        logger.info("\n")
        worker.stop()
        logger.info("")


if __name__ == "__main__":
    asyncio.run(main())
