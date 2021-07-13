"""Configure logging and console output."""

from logging import Logger

import logging
import logging.config

from typing import Tuple


from rich.console import Console
from rich.logging import RichHandler
from rich.traceback import install

from workknow import constants
from workknow import debug


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
    # configure the logger to use the RichHandler, ensuring that
    # there is nicely formatted and colorful output in terminal log
    logging.basicConfig(
        level=debug_level,
        format=constants.logging.Format,
        datefmt="[%X]",
        handlers=[RichHandler()],
    )
    # create a global logger and then make it available with the "Rich" name
    logger = logging.getLogger(constants.logging.Rich)
    return logger


def setup(debug_level: debug.DebugLevel) -> Tuple[Console, Logger]:
    """Perform the setup steps and return a Console for terminal-based display."""
    # configure the use of rich for improved terminal output:
    # --> rich-based tracebacks to enable better debugging on program crash
    configure_tracebacks()
    # --> rich-based logging to improve display of all program console output
    logger = configure_logging(debug_level.value)
    # --> rich-based console to display messages and features in terminal window
    console = Console()
    logger.debug("Finished setting up the console and the logger")
    return console, logger
