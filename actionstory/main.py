"""Command-line interface for the ActionStory program."""

from enum import Enum
from logging import Logger
from typing import Tuple

import typer

from rich.console import Console

from actionstory import configure
from actionstory import constants
from actionstory import create


cli = typer.Typer()


class DebugLevel(str, Enum):
    """The predefined levels for debugging."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


def setup(debug_level: DebugLevel) -> Tuple[Console, Logger]:
    """Perform the setup steps and return a Console for terminal-based display."""
    # configure the use of rich for improved terminal output:
    # --> rich-based tracebacks to enable better debugging on program crash
    configure.configure_tracebacks()
    # --> rich-based logging to improve display of all program console output
    logger = configure.configure_logging(debug_level.value)
    # --> rich-based console to display messages and features in terminal window
    console = Console()
    logger.debug("Finished setting up the console and the logger")
    return console, logger


@cli.command()
def analyze(
    organization: str = typer.Option(...),
    repo: str = typer.Option(...),
    debug_level: DebugLevel = DebugLevel.ERROR,
):
    """Analyze GitHub Action history of repository at URL."""
    # STEP: setup the console and the logger and then create a blank line for space
    console, logger = setup(debug_level)
    # STEP: display the message about the tool
    console.print()
    console.print(constants.actionstory.Emoji + constants.markers.Space + constants.actionstory.Tagline)
    console.print()
    # STEP: create the URL needed for accessing the repository's Action builds
    github_api_url = create.create_github_api_url(organization, repo)
    console.print("Analyzing the build history of the GitHub repository at:")
    console.print(github_api_url, style="link " + github_api_url)
    console.print()
