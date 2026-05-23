import logging
from logging.handlers import RotatingFileHandler
import os
import sys
import threading


LOGGER_NAME = "HotspotApp"


def get_log_path():
    base_dir = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    log_dir = os.path.join(base_dir, "HotspotApp", "logs")
    os.makedirs(log_dir, exist_ok=True)
    return os.path.join(log_dir, "HotspotApp.log")


def setup_logging():
    logger = logging.getLogger(LOGGER_NAME)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    logger.propagate = False

    try:
        handler = RotatingFileHandler(
            get_log_path(),
            maxBytes=256 * 1024,
            backupCount=3,
            encoding="utf-8",
        )
    except OSError:
        handler = logging.NullHandler()

    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    logger.addHandler(handler)

    def log_uncaught_exception(exc_type, exc_value, exc_traceback):
        logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

    def log_thread_exception(args):
        logger.critical(
            "Uncaught thread exception",
            exc_info=(args.exc_type, args.exc_value, args.exc_traceback),
        )

    sys.excepthook = log_uncaught_exception
    if hasattr(threading, "excepthook"):
        threading.excepthook = log_thread_exception

    logger.info("Application starting")
    return logger
