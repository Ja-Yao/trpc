import logging

LOGGER_FORMAT = "%(asctime)s %(levelname)s: %(message)s"

def get_logger(name: str, log_level: int = logging.INFO) -> logging.Logger:
    """Returns a logger with the specified name and log level."""
    logging.basicConfig(level=log_level, format=LOGGER_FORMAT)
    logger = logging.getLogger(name)
    return logger