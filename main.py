import asyncio
import os
import sys
import time
import logging
from pathlib import Path

from utils.config_utils import getConfig
from watchdog.observers import Observer
from har_event_handler import HarEventHandler
from constants import Constants


cfg = getConfig()

os.environ['OPENAI_API_KEY'] = Constants.OPENAI_API_KEY

# Ensure directories exist
cfg.watch_dir.mkdir(parents=True, exist_ok=True)
cfg.process_dir.mkdir(parents=True, exist_ok=True)
cfg.error_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=getattr(logging, cfg.log_level.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger("har-agent")

async def main():
    logger.info("Starting HAR agent. Watch dir: %s", cfg.watch_dir)
    event_handler = HarEventHandler()
    observer = Observer()
    observer.schedule(event_handler, str(cfg.watch_dir), recursive=False)
    logger.info("Observer scheduled")
    observer.start()
    logger.info("Observer started")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        observer.stop()
        observer.join()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception:
        logger.exception("Fatal error in HAR agent. Please relaunch the agent.")
        sys.exit(1)