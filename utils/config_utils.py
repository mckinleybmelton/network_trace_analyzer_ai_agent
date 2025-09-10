import os
from pathlib import Path
from dataclasses import dataclass
from constants import Constants

# --------------- Configuration ----------------

@dataclass
class Config:
    watch_dir: Path
    process_dir: Path
    error_dir: Path
    log_level: str = "INFO"
    file_settle_seconds: float = 1.0
    max_wait_seconds: float = 30.0
    valid_extension: str = ".har"


    @staticmethod
    def from_env() -> 'Config':
        base = Path(os.getenv('WATCH_DIR', Constants.WATCH_DIR)).resolve()
        output = Path(os.getenv('OUTPUT_DIR', Constants.PROCESS_DIR)).resolve()
        return Config(
            watch_dir=base,
            process_dir=Path(os.getenv("PROCESS_DIR", output / "process")).resolve(),
            error_dir=Path(os.getenv("ERROR_DIR", output / "error")).resolve(),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            file_settle_seconds=float(os.getenv("FILE_SETTLE_SECONDS", "1.0")),
            max_wait_seconds=float(os.getenv("MAX_WAIT_SECONDS", "30.0")),
            valid_extension=os.getenv("VALID_EXTENSION", ".har").lower(),
        )
    
# --------------- Helper Method ----------------

def getConfig():
    return Config.from_env() 