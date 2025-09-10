import logging
from pathlib import Path

from utils.config_utils import getConfig
from utils.file_utils import handle_har_file
from watchdog.events import FileSystemEventHandler, FileSystemEvent

cfg = getConfig()

logging.basicConfig(
    level=getattr(logging, cfg.log_level.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger("har-agent")

# ---------- Watcher ----------

class HarEventHandler(FileSystemEventHandler):
    async def on_created(self, event: FileSystemEvent):
        logger.info("create event registered: %s", event.src_path)
        self._maybe_process(event)

    async def on_moved(self, event: FileSystemEvent):
        logger.info("move event registered: %s -> %s", event.src_path, getattr(event, "dest_path", ""))
        self._maybe_process(event)

    async def _maybe_process(self, event: FileSystemEvent):
        if event.is_directory:
            return
        path = Path(event.src_path)
        logger.info("processing file: %s", path)
        if path.suffix.lower() == cfg.valid_extension:
            try:
                handle_har_file(path)
            except Exception:
                logger.exception("Unhandled error processing %s", path)
        else:
            logger.info("Ignoring non-HAR file: %s", path)