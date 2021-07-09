"""Command-line interface for the ActionStory program."""

from enum import Enum
from logging import Logger
from typing import Tuple

import typer

from rich.console import Console
from rich.pretty import pprint

from actionstory import configure
from actionstory import constants
from actionstory import process
from actionstory import request


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
    console.print(
        constants.actionstory.Emoji
        + constants.markers.Space
        + constants.actionstory.Tagline
    )
    console.print()
    # STEP: create the URL needed for accessing the repository's Action builds
    github_api_url = process.create_github_api_url(organization, repo)
    console.print("Analyzing the build history of the GitHub repository at:")
    console.print(github_api_url, style="link " + github_api_url)
    console.print()
    # STEP: access the JSON file that contains the build history
    json_responses = request.request_json_from_github(github_api_url)
    console.print(
        f"Downloaded a total of {process.count_individual_builds(json_responses)} build records that look like:"
    )
    # STEP: print debugging information in a summarized fashion
    pprint(json_responses, max_length=3)
    console.print()
    console.print("The first build records looks like:")
    pprint(json_responses[0][0], max_length=25)
    logger.debug(json_responses[0][0])
    console.print()
    # pprint(json_responses[0][0])
