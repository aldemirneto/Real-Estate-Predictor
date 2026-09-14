import logging
import sys


def _setup_logger() -> logging.Logger:
    logger = logging.getLogger("real_estate")
    if logger.handlers:
        return logger
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    )
    logger.addHandler(handler)
    return logger


class Logging:
    def __init__(self):
        self._logger = _setup_logger()

    def log(self, message):
        self._logger.info(message)

    def error(self, message):
        self._logger.error(message)

    def log_email(self, email):
        self._logger.info(f"[EMAIL] {email}")
