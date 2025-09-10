import sys
import time
import logging
from pathlib import Path

from utils.config_utils import getConfig
from utils.file_utils import handle_har_file
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

cfg = getConfig()

# Ensure directories exist
cfg.watch_dir.mkdir(parents=True, exist_ok=True)
cfg.process_dir.mkdir(parents=True, exist_ok=True)
cfg.error_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=getattr(logging, cfg.log_level.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger("har-agent")

# ---------- Watcher ----------

class HarEventHandler(FileSystemEventHandler):
    def on_created(self, event: FileSystemEvent):
        logger.info("create event registered: %s", event.src_path)
        self._maybe_process(event)

    def on_moved(self, event: FileSystemEvent):
        logger.info("move event registered: %s -> %s", event.src_path, getattr(event, "dest_path", ""))
        self._maybe_process(event)

    def _maybe_process(self, event: FileSystemEvent):
        if event.is_directory:
            return
        path = Path(event.src_path)
        logger.info("processing file: %s", path)
        if path.suffix.lower() == cfg.valid_extension:
            try:
                handle_har_file(path)
            except Exception:
                logger.exception("Unhandled error processing %s", path)

def run():
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
        run()
    except Exception:
        logger.exception("Fatal error in HAR agent. Please relaunch the agent.")
        sys.exit(1)