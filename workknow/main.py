"""Command-line interface for the workknow program."""

from enum import Enum
from logging import Logger
from pathlib import Path

from typing import List
from typing import Tuple

import pandas
import typer

from rich.console import Console
from rich.pretty import pprint

from workknow import configure
from workknow import constants
from workknow import files
from workknow import produce
from workknow import request


cli = typer.Typer()


class DebugLevel(str, Enum):
    """The predefined levels for debugging."""

    DEBUG = constants.logging.Debug
    INFO = constants.logging.Info
    WARNING = constants.logging.Warning
    ERROR = constants.logging.Error
    CRITICAL = constants.logging.Critical


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
    repo_urls: List[str],
    repos_csv_file: Path = typer.Option(None),
    results_dir: Path = typer.Option(None),
    debug_level: DebugLevel = DebugLevel.ERROR,
    save: bool = typer.Option(False),
):
    """Analyze GitHub Action history of repository at URL."""
    # STEP: setup the console and the logger and then create a blank line for space
    console, logger = setup(debug_level)
    # STEP: display the messages about the tool
    console.print()
    console.print(
        constants.workknow.Emoji + constants.markers.Space + constants.workknow.Tagline
    )
    console.print(constants.workknow.Website)
    console.print()
    # create empty lists of the data frames
    repository_urls_dataframes_workflows = []
    repository_urls_dataframes_commits = []
    # read the CSV file and extract its data into a Pandas DataFrame
    provided_urls_data_frame = files.read_csv_file(repos_csv_file)
    provided_url_list = produce.extract_repo_urls_list(provided_urls_data_frame)
    logger.debug(repo_urls)
    repo_urls = list(repo_urls)
    repo_urls.extend(provided_url_list)
    logger.debug(repo_urls)
    merged_repo_urls = produce.flatten(repo_urls)
    logger.debug(merged_repo_urls)
    # iterate through all of the repo_urls provided on the command-line or in the CSV file
    for repo_url in merged_repo_urls:
        # STEP: create the URL needed for accessing the repository's Action builds
        organization, repo = produce.parse_github_url(repo_url)
        if organization is not None and repo is not None:
            github_api_url = produce.create_github_api_url(organization, repo)
            console.print(
                ":runner: Analyzing the workflow history of the GitHub repository at:"
            )
            console.print(github_api_url, style="link " + github_api_url)
            console.print()
            # STEP: access the JSON file that contains the build history
            json_responses = request.request_json_from_github(github_api_url)
            console.print(
                f":inbox_tray: Downloaded a total of {produce.count_individual_builds(json_responses)} records that look like:\n"
            )
            # STEP: print debugging information in a summarized fashion
            pprint(json_responses, max_length=constants.github.Maximum_Length_All)
            console.print()
            console.print(":lion_face: The first workflow record looks like:\n")
            pprint(
                json_responses[0][0], max_length=constants.github.Maximum_Length_Record
            )
            logger.debug(json_responses[0][0])
            console.print()
            # pprint(json_responses[0][0])
            # STEP: create the workflows DataFrame
            workflows_dataframe = produce.create_workflows_dataframe(
                organization, repo, repo_url, json_responses
            )
            repository_urls_dataframes_workflows.append(workflows_dataframe)
            # STEP: create the commit details DataFrame
            commits_dataframe = produce.create_commits_dataframe(
                organization, repo, repo_url, json_responses
            )
            repository_urls_dataframes_commits.append(commits_dataframe)
            # STEP: save the workflows DataFrame when saving is stipulated and
            # the results directory is valid for the user's file system
            if save and files.confirm_valid_directory(results_dir):
                # save the workflows DataFrame
                console.print(
                    f":sparkles: Saving data for {organization}/{repo} in the directory {str(results_dir).strip()}"
                )
                console.print("\t... Saving the workflows data.")
                files.save_dataframe(
                    results_dir,
                    organization,
                    repo,
                    constants.filesystem.Workflows,
                    workflows_dataframe,
                )
                # save the commits DataFrame
                console.print("\t... Saving the commits data.")
                files.save_dataframe(
                    results_dir,
                    organization,
                    repo,
                    constants.filesystem.Commits,
                    commits_dataframe,
                )
            else:
                # explain that the save could not work correctly due to invalid results directory
                console.print(
                    f"Could not save workflow and commit data for {organization}/{repo} in the directory {str(results_dir).strip()}"
                )
            console.print()
    console.print(":runner: Creating combined data sets across all repositories.")
    console.print()
    all_workflows_dataframe = pandas.concat(repository_urls_dataframes_workflows)
    all_commits_dataframe = pandas.concat(repository_urls_dataframes_commits)
    if save and files.confirm_valid_directory(results_dir):
        # save the workflows DataFrame
        console.print(
            f":sparkles: Saving combined data for all repositories in the directory {str(results_dir).strip()}"
        )
        # save the all workflows DataFrame
        console.print("\t... Saving combined workflows data for all repositories.")
        files.save_dataframe_all(
            results_dir,
            constants.filesystem.Workflows,
            all_workflows_dataframe,
        )
        # save the commits DataFrame
        console.print("\t... Saving combined commits data for all repositories.")
        files.save_dataframe_all(
            results_dir,
            constants.filesystem.Commits,
            all_commits_dataframe,
        )
    else:
        # explain that the save could not work correctly due to invalid results directory
        console.print(
            f"Could not save workflow and commit details for {organization}/{repo} in the directory {str(results_dir).strip()}"
        )
    console.print()
