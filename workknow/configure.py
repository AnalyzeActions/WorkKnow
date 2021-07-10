"""Configure logging and console output."""

import logging
import logging.config

from rich.logging import RichHandler
from rich.traceback import install

from workknow import constants


def configure_tracebacks() -> None:
    """Configure stack tracebacks arising from a crash to use rich."""
    install()


def configure_logging(
    debug_level: str = constants.logging.Default_Logging_Level,
) -> logging.Logger:
    """Configure standard Python logging package to use rich."""
    logging.basicConfig(
        level=debug_level,
        format=constants.logging.Format,
        datefmt="[%X]",
        handlers=[RichHandler()],
    )
    # create a global logger and then make it available with the "Rich" name
    logger = logging.getLogger(constants.logging.Rich)
    return logger
