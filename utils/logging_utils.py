import logging

from utils.config_utils import getConfig

cfg = getConfig()

def getLogger():
    logging.basicConfig(
        level=getattr(logging, cfg.log_level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(message)s"
    )
    return logging.getLogger("har-agent")
