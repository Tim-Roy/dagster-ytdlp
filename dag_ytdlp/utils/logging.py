import logging
from os import environ
from pathlib import Path

from .datetime import now

LOG_PATH = environ["LOG_HOME"]
NOW = now()


def setup_logging():
    """Initialize logging for compatiblity with dagster."""
    logger = logging.getLogger("ytdl_logger")
    log_fname = f"{LOG_PATH}/ytdl/{NOW}.log"
    Path(log_fname).touch(exist_ok=True)
    handler = logging.FileHandler(log_fname, mode="a", encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s", datefmt="%Y-%m-%d %I:%M:%S %p")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    return logger
