import logging

from rich.logging import RichHandler

from config import LOG_LEVEL


def setup_logger(name: str = "dsa_agent", level: str = LOG_LEVEL) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    if not logger.handlers:
        handler = RichHandler(
            rich_tracebacks=True,
            show_time=True,
            show_level=True,
            show_path=True,
            markup=True,
        )
        formatter = logging.Formatter("%(name)s: %(message)s", datefmt="[%X]")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


logger = setup_logger()
