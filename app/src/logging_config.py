import logging
import os
from pythonjsonlogger import jsonlogger


def configure_logging():
    logger = logging.getLogger()
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    logger.setLevel(level)
    if not logger.handlers:
        handler = logging.StreamHandler()
        fmt = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s')
        handler.setFormatter(fmt)
        logger.addHandler(handler)

