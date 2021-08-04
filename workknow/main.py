"""Command-line interface for the workknow program."""

from pathlib import Path

from typing import List

import pandas
import typer

from rich.pretty import pprint

from workknow import concatenate
from workknow import configure
from workknow import constants
from workknow import debug
from workknow import display
from workknow import environment
from workknow import files
from workknow import produce
from workknow import release
from workknow import request


# create a Typer object to supper the command-line interface
cli = typer.Typer()


@cli.command()
def download(
    repo_urls: List[str] = typer.Option([]),
    repos_csv_file: Path = typer.Option(None),
    results_dir: Path = typer.Option(None),
    env_file: Path = typer.Option(None),
    combine: bool = typer.Option(False),
    peek: bool = typer.Option(False),
    save: bool = typer.Option(False),
    debug_level: debug.DebugLevel = debug.DebugLevel.ERROR,
):
    """Download the GitHub Action workflow history of repositories in URL list and CSV file."""
    # STEP: setup the console and the logger and then create a blank line for space
    console, logger = configure.setup(debug_level)
    # STEP: load the execution environment to support GitHub API access
    environment.load_environment(env_file, logger)
    # display the messages about the tool
    display.display_tool_details(debug_level)
    # create empty lists of the data frames
    repository_urls_dataframes_workflows = []
    repository_urls_dataframes_commits = []
    # assume that the repos_csv_file was not specified and prove otherwise
    repos_csv_file_valid = False
    # STEP: get any rate limit details and stop using the program
    # if it is in danger of being rate limited and not having data
    request.get_rate_limit_details()
    # STEP: read the CSV file and extract its data into a Pandas DataFrame
    # there is a valid CSV file of repository data
    # create an empty DataFrame in case the CSV file specified on the
    # command-line is not valid or, alternatively, it is not specified at all
    provided_urls_data_frame = pandas.DataFrame()
    if files.confirm_valid_file(repos_csv_file):
        repos_csv_file_valid = True
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
    # the user did, in fact, specify repositories for analysis
    if len(repo_urls) != 0:
        # display debugging information about the data frames
        logger.debug(repo_urls)
        # iterate through all of the repo_urls provided on the command-line or in the CSV file
        for repo_url in repo_urls:
            # STEP: create the URL needed for accessing the repository's Action builds
            organization, repo = produce.parse_github_url(repo_url)
            if organization is not None and repo is not None:
                github_api_url = produce.create_github_api_url(organization, repo)
                console.print()
                console.print(
                    ":runner: Downloading the workflow history of the GitHub repository at:"
                )
                console.print(github_api_url, style="link " + github_api_url)
                console.print()
                # STEP: access the JSON file that contains the build history
                (valid, _, _, json_responses) = request.request_json_from_github(
                    github_api_url, console
                )
                # the data returned from the API is valid; this means that either no difficulties
                # were encountered or, alternatively, there were difficulties but a series of
                # one or more retries allowed for the "waiting out" of the problem and the
                # ultimate collection of valid data that can now be extracted and saved
                if valid:
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
                        pprint(
                            json_responses,
                            max_length=constants.github.Maximum_Length_All,
                        )
                        if produce.count_individual_builds(json_responses) != 0:
                            console.print()
                            console.print(
                                ":lion_face: The first workflow record looks like:\n"
                            )
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
                        organization, repo, repo_url, github_api_url, json_responses
                    )
                    repository_urls_dataframes_workflows.append(workflows_dataframe)
                    # STEP: create the commit details DataFrame
                    commits_dataframe = produce.create_commits_dataframe(
                        organization, repo, repo_url, github_api_url, json_responses
                    )
                    repository_urls_dataframes_commits.append(commits_dataframe)
                    # STEP: save the workflows DataFrame when saving is stipulated and
                    # the results directory is valid for the user's file system
                    # save the workflows DataFrame
                    if save:
                        # the directory is valid so attempt a save to file system
                        if files.confirm_valid_directory(results_dir):
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
                    request.get_rate_limit_wait_time_and_wait(rate_limit_dict)
                else:
                    console.print()
                    # explain that the save could not work correctly due to invalid results directory
                    console.print(
                        f":grimacing_face: Could not download workflow and commit details for {organization}/{repo}"
                    )
        # now that WorkKnow is finished with the processing of each of the individual repositories and
        # they are stored in the currently in-memory DataFrames, save the required data to disk;
        # however, only save all of the results in the file system if the save parameter is specified
        if save:
            if files.confirm_valid_directory(results_dir):
                # finished processing all of the individual repositories and now ready to create
                # the "combined" data sets that include data for every repository subject to analysis
                console.print()
                console.print(
                    ":runner: Creating combined data sets across all repositories"
                )
                # combine all of the individual DataFrames for the workflow data
                all_workflows_dataframe = pandas.concat(
                    repository_urls_dataframes_workflows
                )
                # combine all of the individual DataFrames for the commit data
                all_commits_dataframe = pandas.concat(
                    repository_urls_dataframes_commits
                )
                # combine all of the dictionaries in the list to create DataFrame of workflow record data
                all_workflow_record_counts_dataframe = pandas.DataFrame(
                    repo_url_workflow_record_list
                )
                console.print()
                # Combine the data in the two data frames so that the count data (i.e., the number of
                # workflow builds) is joined to the data about the repositories, as created by the
                # project that reports data about the criticality of open-source projects. WorkKnow
                # can only take this step if the user specified the CSV file from the criticality
                # score project that contains multiple additional columns of data
                if repos_csv_file_valid:
                    all_workflow_record_counts_dataframe_merged = (
                        produce.merge_repo_urls_with_count_data(
                            provided_urls_data_frame,
                            all_workflow_record_counts_dataframe,
                        )
                    )
                # there was no specification of a CSV file on the command line and thus there is
                # no extra data to record; in this situation the "merged" data file that will be
                # saved is only the one that has the counts of the workflow builds for each project
                else:
                    all_workflow_record_counts_dataframe_merged = (
                        all_workflow_record_counts_dataframe
                    )
                # save the all records count DataFrame
                # note that it is acceptable to save this
                # DataFrame since it is always smaller in size
                console.print(
                    f":sparkles: Saving combined data for all repositories in the directory {str(results_dir).strip()}"
                )
                console.print(
                    f"{constants.markers.Tab}... Saving combined workflow count data for all repositories"
                )
                files.save_dataframe_all(
                    results_dir,
                    constants.filesystem.Counts,
                    all_workflow_record_counts_dataframe_merged,
                )
                # combine the individual data files into the (very very) large data files that include
                # details about each of the repositories; note that the --combine argument will create
                # data files that cannot be automatically uploaded to a GitHub repository due to the
                # fact that they are going to be over 100 MB in size and thus require GitHub LFS
                if combine:
                    # save the all workflows DataFrame
                    console.print(
                        f"{constants.markers.Tab}... Saving combined workflows data for all repositories"
                    )
                    files.save_dataframe_all(
                        results_dir,
                        constants.filesystem.Workflows,
                        all_workflows_dataframe,
                    )
                    # save the all commits DataFrame
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
                console.print()
                # explain that the save could not work correctly due to invalid results directory
                console.print(
                    f":grimacing_face: Could not save workflow and commit details in the directory {str(results_dir).strip()}"
                )
                console.print(
                    constants.markers.Space
                    + constants.markers.Space
                    + constants.markers.Space
                    + "Did you specify a valid results directory?"
                    + constants.markers.Newline
                    + constants.markers.Newline
                    + ":sad_but_relieved_face: Exiting now!"
                )
            console.print()
            request.get_rate_limit_details()
    # there were no valid repository URLs provided on the command-line so workflow analysis could not proceed
    else:
        console.print(
            ":grimacing_face: Did not find any GitHub repositories for workflow analysis!"
        )
        console.print(
            constants.markers.Space
            + constants.markers.Space
            + constants.markers.Space
            + "Did you provide at least one repository URL?"
            + constants.markers.Newline
            + constants.markers.Newline
            + ":sad_but_relieved_face: Exiting now!"
        )
        console.print()


@cli.command()
def upload(
    repo_url: str,
    semver: str,
    results_dir: Path,
    env_file: Path = typer.Option(None),
    debug_level: debug.DebugLevel = debug.DebugLevel.ERROR,
):
    """Upload to a GitHub release the data in the results directory."""
    # STEP: setup the console and the logger instance
    console, logger = configure.setup(debug_level)
    # STEP: load the execution environment to support GitHub API access
    environment.load_environment(env_file, logger)
    # STEP: display the messages about the tool
    display.display_tool_details(debug_level)
    # extract the organization and the repository from the repository URL
    github_organization, github_repository = produce.parse_github_url(repo_url)
    # STEP: perform the upload to GitHub repository
    # the extract github_organization and github_repository are correct
    # and it is possible to move onto the uploading to GitHub step
    if github_organization is not None and github_repository is not None:
        # display diagnostic message in the console
        console.print(
            f":runner: Uploading all workflow history data to the GitHub repository at: {repo_url}"
        )
        # create a blank line before the progress bar created by perform_github_upload
        console.print()
        release.perform_github_upload(
            repo_url, github_organization, github_repository, semver, results_dir
        )
        # create a blank line after the progress bar created by perform_github_upload
        console.print()
    else:
        console.print(
            f":grimacing_face: Unable to access GitHub repository at {repo_url}"
        )


@cli.command()
def combine(
    csv_dir: Path = typer.Option(None),
    results_dir: Path = typer.Option(None),
    env_file: Path = typer.Option(None),
    save: bool = typer.Option(False),
    debug_level: debug.DebugLevel = debug.DebugLevel.ERROR,
):
    """Combine the downloaded GitHub Action workflow and commit history for all projects in a specified directory."""
    # STEP: setup the console and the logger and then create a blank line for space
    console, logger = configure.setup(debug_level)
    # STEP: load the execution environment to support GitHub API access
    environment.load_environment(env_file, logger)
    # STEP: display the messages about the tool
    display.display_tool_details(debug_level)
    # STEP: the directory is valid so attempt to load each file and summarize
    if files.confirm_valid_directory(csv_dir):
        # display a diagnostic message to indicate that WorkKnow will create
        # the summarized data files and then save them to the results directory
        console.print()
        console.print(
            f":runner: Combining commit and workflow histories for CSV files stored in {csv_dir}"
        )
        console.print()
        # summarize all of the files that are found in the CSV file directory
        (
            data_frame_counts,
            data_frame_commits,
            data_frame_workflows,
        ) = concatenate.combine_files_in_directory(csv_dir)
        logger.debug(data_frame_counts)
        # save the combined data files to the disk in the results directory
        if save:
            console.print(
                f":sparkles: Saving combined commit and workflow histories in {results_dir}"
            )
            console.print()
            # the results directory is a valid directory that can store the files
            if files.confirm_valid_directory(results_dir):
                console.print(
                    f"{constants.markers.Tab}... Saving combined workflow count data for all repositories"
                )
                # save the Pandas DataFrame that contains the commits data;
                # the name of the file is "All-Counts.csv"
                files.save_dataframe_all(
                    results_dir,
                    constants.filesystem.Counts,
                    data_frame_counts,
                )
                console.print(
                    f"{constants.markers.Tab}... Saving combined workflows data for all repositories"
                )
                # save the Pandas DataFrame that contains the workflow data;
                # the name of the file is "All-Workflows.csv"
                files.save_dataframe_all(
                    results_dir,
                    constants.filesystem.Workflows,
                    data_frame_workflows,
                )
                console.print(
                    f"{constants.markers.Tab}... Saving combined commits data for all repositories"
                )
                # save the Pandas DataFrame that contains the workflow data;
                # the name of the file is "All-Commits.csv"
                files.save_dataframe_all(
                    results_dir,
                    constants.filesystem.Commits,
                    data_frame_commits,
                )
                console.print()


@cli.command()
def analyze(debug_level: debug.DebugLevel = debug.DebugLevel.ERROR):
    """Analyze already the downloaded data."""
    # setup the console and the logger instance
    console, _ = configure.setup(debug_level)
    # STEP: display the messages about the tool
    display.display_tool_details(debug_level)
    console.print(":person_shrugging: Sorry, this feature does not yet exist.")
    console.print()
