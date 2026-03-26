import sys
import os
from loguru import logger
from datetime import datetime

log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

logger.remove()

logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level="INFO"
)

logger.add(
    os.path.join(log_dir, "intelli_{time:YYYY-MM-DD}.log"),
    rotation="1 day",
    retention="7 days",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
)

logger.info("Logger initialized")
