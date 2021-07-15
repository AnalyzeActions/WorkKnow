"""Command-line interface for the workknow program."""

from pathlib import Path

from typing import List

import pandas
import typer

from rich.pretty import pprint

from workknow import configure
from workknow import constants
from workknow import debug
from workknow import display
from workknow import environment
from workknow import files
from workknow import produce
from workknow import request


# create a Typer object to supper the command-line interface
cli = typer.Typer()


@cli.command()
def download(
    repo_urls: List[str],
    repos_csv_file: Path = typer.Option(None),
    results_dir: Path = typer.Option(None),
    env_file: Path = typer.Option(None),
    peek: bool = typer.Option(False),
    save: bool = typer.Option(False),
    debug_level: debug.DebugLevel = debug.DebugLevel.ERROR,
):
    """Download the GitHub Action workflow history of repositories in URL list and CSV file."""
    # STEP: setup the console and the logger and then create a blank line for space
    console, logger = configure.setup(debug_level)
    # STEP: load the execution environment to support GitHub API access
    environment.load_environment(env_file, logger)
    # STEP: display the messages about the tool
    display.display_tool_details(debug_level)
    # STEP: create empty lists of the data frames
    repository_urls_dataframes_workflows = []
    repository_urls_dataframes_commits = []
    # STEP: get any rate limit details and stop using the program
    # if it is in danger of being rate limited and not having data
    request.get_rate_limit_details()
    # STEP: read the CSV file and extract its data into a Pandas DataFrame
    # there is a valid CSV file of repository data
    if files.confirm_valid_file(repos_csv_file):
        # read the CSV file and produce a Pandas DataFrame out of it
        provided_urls_data_frame = files.read_csv_file(repos_csv_file)
        # extract the repository URLs from the data frame;
        # note that the (documented) assumption is that the CSV file
        # must have a column called "url" that contains the URLs and
        # that the WorkKnow will ignore all other data inside of the CSV file
        provided_url_list = produce.extract_repo_urls_list(provided_urls_data_frame)
        # since Typer seems to convert repo_urls into a tuple, convert it to a list
        repo_urls = list(repo_urls)
        # add the URLs extracted from the CSV file into the repo_urls list
        repo_urls.extend(provided_url_list)
        # display debugging information about the data frames
        logger.debug(repo_urls)
    repo_url_workflow_record_list = []
    # iterate through all of the repo_urls provided on the command-line or in the CSV file
    for repo_url in repo_urls:
        # STEP: create the URL needed for accessing the repository's Action builds
        organization, repo = produce.parse_github_url(repo_url)
        if organization is not None and repo is not None:
            github_api_url = produce.create_github_api_url(organization, repo)
            console.print(
                ":runner: Downloading the workflow history of the GitHub repository at:"
            )
            console.print(github_api_url, style="link " + github_api_url)
            console.print()
            # STEP: access the JSON file that contains the build history
            json_responses = request.request_json_from_github(github_api_url, console)
            # STEP: collect data about the number of workflow records in the JSON responses
            repo_url_workflow_record_dict = (
                produce.create_workflow_record_count_dictionary(
                    organization, repo, repo_url, github_api_url, json_responses
                )
            )
            repo_url_workflow_record_list.append(repo_url_workflow_record_dict)
            # STEP: print some details about the completed download
            # --> display a peek into the downloaded data structure
            if peek:
                console.print()
                console.print(
                    f":inbox_tray: Downloaded a total of {produce.count_individual_builds(json_responses)} records that each look like:\n"
                )
                # STEP: print debugging information in a summarized fashion
                pprint(json_responses, max_length=constants.github.Maximum_Length_All)
                console.print()
                console.print(":lion_face: The first workflow record looks like:\n")
                pprint(
                    json_responses[0][0],
                    max_length=constants.github.Maximum_Length_Record,
                )
                logger.debug(json_responses[0][0])
                console.print()
            # --> the program should not display a peek into the downloaded data structure
            else:
                console.print()
                console.print(
                    f":inbox_tray: Downloaded a total of {produce.count_individual_builds(json_responses)} records\n"
                )
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
                console.print("\t... Saving the workflows data")
                files.save_dataframe(
                    results_dir,
                    organization,
                    repo,
                    constants.filesystem.Workflows,
                    workflows_dataframe,
                )
                # save the commits DataFrame
                console.print("\t... Saving the commits data")
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
            # before going on to the next GitHub repository, ensure that the program
            # is not about to be rate limited, which will cause a crash. If a rate
            # limit is imminent then sleep for the time remaining until GitHub resets.
            rate_limit_dict = request.get_rate_limit_details()
            request.get_rate_limit_wait_time(rate_limit_dict)
    # finished processing all of the individual repositories and now ready to create
    # the "combined" data sets that include data for every repository subject to analysis
    console.print(":runner: Creating combined data sets across all repositories")
    console.print()
    # combine all of the individual DataFrames for the workflow data
    all_workflows_dataframe = pandas.concat(repository_urls_dataframes_workflows)
    # combine all of the individual DataFrames for the commit data
    all_commits_dataframe = pandas.concat(repository_urls_dataframes_commits)
    # combine all of the dictionaries in the list to create DataFrame of workflow record data
    all_workflow_record_counts_dataframe = pandas.DataFrame(
        repo_url_workflow_record_list
    )
    # save all of the results in the file system if the save parameter is specified
    if save and files.confirm_valid_directory(results_dir):
        # save the workflows DataFrame
        console.print(
            f":sparkles: Saving combined data for all repositories in the directory {str(results_dir).strip()}"
        )
        # save the all records count DataFrame
        console.print(
            f"{constants.markers.Tab}... Saving combined workflow count data for all repositories"
        )
        files.save_dataframe_all(
            results_dir,
            constants.filesystem.Counts,
            all_workflow_record_counts_dataframe,
        )
        # save the all workflows DataFrame
        console.print(
            f"{constants.markers.Tab}... Saving combined workflows data for all repositories"
        )
        files.save_dataframe_all(
            results_dir,
            constants.filesystem.Workflows,
            all_workflows_dataframe,
        )
        # save the commits DataFrame
        console.print(
            f"{constants.markers.Tab}... Saving combined commits data for all repositories"
        )
        files.save_dataframe_all(
            results_dir,
            constants.filesystem.Commits,
            all_commits_dataframe,
        )
        # save a .zip file of all of the CSV files in the results directory
        console.print()
        console.print(
            f":sparkles: Saving a Zip file of all results in the directory {str(results_dir).strip()}"
        )
        results_file_list = files.create_results_zip_file_list(results_dir)
        files.create_results_zip_file(results_dir, results_file_list)
    else:
        # explain that the save could not work correctly due to invalid results directory
        console.print(
            f":grimacing_face: Could not save workflow and commit details in the directory {str(results_dir).strip()}"
        )
    console.print()
    request.get_rate_limit_details()


@cli.command()
def analyze(debug_level: debug.DebugLevel = debug.DebugLevel.ERROR):
    """Analyze already the downloaded data."""
    # setup the console and the logger instance
    _, _ = configure.setup(debug_level)
