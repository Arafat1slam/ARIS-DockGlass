"""Logger setup for ARIS DockGlass."""
import logging
import os
from logging.handlers import RotatingFileHandler
import re
from .paths import get_logs_dir

class PathRedactingFormatter(logging.Formatter):
    """Formatter that redacts full paths, keeping only filenames."""
    
    def format(self, record: logging.LogRecord) -> str:
        message = super().format(record)
        # Redact Windows paths (e.g., C:\foo\bar.txt -> bar.txt)
        message = re.sub(r'(?:[a-zA-Z]:\\|\\\\)(?:[^\\]+\\)*([^\\]+)', r'\1', message)
        return message

def setup_logger(level: int = logging.INFO) -> logging.Logger:
    """Configure and return the main rotating logger."""
    logger = logging.getLogger("ARIS_DockGlass")
    logger.setLevel(level)
    
    if not logger.handlers:
        log_file = os.path.join(get_logs_dir(), "app.log")
        
        # 5 MB x 3 files
        handler = RotatingFileHandler(
            log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
        )
        
        formatter = PathRedactingFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger

logger = setup_logger()
setup_logging = setup_logger

def get_logger(name: str = None) -> logging.Logger:
    return logging.getLogger(name or "ARIS_DockGlass")
