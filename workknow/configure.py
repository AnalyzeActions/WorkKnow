"""Configure logging and console output."""

import logging
import logging.config

from rich.logging import RichHandler
from rich.traceback import install

from workknow import constants


def configure_tracebacks() -> None:
    """Configure stack tracebacks arising from a crash to use rich."""
    # Use the install function provided by rich to get colorful
    # and nicely labelled and organized tracebacks when program crashes.
    # Note that the tracebacks will not be rich-ified before this
    # function is called and thus an early program crash will lead to
    # a traceback that is, sadly, not rich-ified
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
