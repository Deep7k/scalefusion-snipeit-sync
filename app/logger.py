import os
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

def setup_logger(log_level: str) -> logging.Logger:
    log_format = "%(asctime)s [%(levelname)s] %(message)s"
    os.makedirs("logs", exist_ok=True)
    log_filename = datetime.now().strftime("logs/assetsync-%Y%m%d.log")

    file_handler = TimedRotatingFileHandler(
        log_filename,
        when="midnight",
        interval=1,
        backupCount=7,
        encoding="utf-8",
        maxBytes=10*1024*1024
    )
    file_handler.suffix = "%Y%m%d"
    file_handler.setFormatter(logging.Formatter(log_format))

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format))

    logging.basicConfig(
        level=getattr(logging, log_level),
        handlers=[console_handler, file_handler]
    )

    return logging.getLogger(__name__)