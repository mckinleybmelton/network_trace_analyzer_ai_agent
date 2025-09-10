import json
import time
import traceback
from typing import Optional
from pathlib import Path

from skills.har_analyzer import analyze_har
from utils.config_utils import getConfig
from utils.logging_utils import getLogger

logger = getLogger()
cfg = getConfig()

# Wait until file is stable (not changing size) before processing
async def wait_until_file_is_stable(path: Path, settle_seconds: float, max_wait_seconds: float) -> bool:
    """Wait until file size stops changing to avoid parsing a partial write."""
    logger.debug("Waiting for file to stabilize: %s", path)
    elapsed = 0.0
    last_size = -1
    while elapsed < max_wait_seconds:
        try:
            size = path.stat().st_size
        except FileNotFoundError:
            time.sleep(0.2)
            elapsed += 0.2
            continue
        if size == last_size:
            return True
        last_size = size
        time.sleep(settle_seconds)
        elapsed += settle_seconds
    logger.warning("File did not stabilize in time: %s", path)
    return False

# Load HAR file safely
async def load_har(path: Path) -> Optional[dict]:
    with path.open("r", encoding="utf-8", errors="replace") as f:
        return json.load(f)

# Main logic to handle processing of HAR file
async def handle_har_file(path: Path):
    logger.info("Processing HAR: %s", path)
    if not wait_until_file_is_stable(path, cfg.file_settle_seconds, cfg.max_wait_seconds):
        logger.error("Skipping unstable file: %s", path)
        return

    try:
        har = load_har(path)
    except Exception as e:
        logger.exception("Failed to parse HAR: %s", e)
        move_to = cfg.error_dir / path.name
        path.replace(move_to)
        return

    try:
        logger.debug("Entering analyze_har")
        results = analyze_har(har)
        logger.info("Analysis summary: %s", results)
        move_to = cfg.process_dir / path.name
        # Save results to a text file in the move_to directory
        results_file = move_to.with_suffix('.txt')
        with results_file.open('w', encoding='utf-8') as f:
            f.write(str(results))
        path.replace(move_to)
        logger.info("Processed & moved to: %s; Results saved to: %s", move_to, results_file)
    except Exception as e:
        logger.exception("Analysis failed: %s", e)
        move_to = cfg.error_dir / path.name
        # Save results to a text file in the move_to directory
        results_file = move_to.with_suffix('.txt')
        with results_file.open('w', encoding='utf-8') as f:
            f.write('Exception: ' + str(e) + '\n')
            f.write(traceback.format_exc())
        path.replace(move_to)
        logger.info("Moved failed HAR to error dir: %s; Error details saved to: %s", move_to, results_file)