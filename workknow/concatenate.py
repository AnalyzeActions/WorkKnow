"""Combine data in CSV files in provided directories and create Pandas DataFrames."""

import logging

from pathlib import Path

from typing import Dict
from typing import List
from typing import Tuple
from typing import Union

import pandas

from rich.progress import BarColumn
from rich.progress import Progress
from rich.progress import TimeRemainingColumn
from rich.progress import TimeElapsedColumn

from workknow import configure
from workknow import constants


def combine_files_in_directory(
    csv_directory: Path,
) -> Tuple[pandas.DataFrame, pandas.DataFrame, pandas.DataFrame]:
    """Combine all of the CSV files inside of a directory."""
    logger = logging.getLogger(constants.logging.Rich)
    console = configure.setup_console()
    data_frame_list_commits: List[pandas.DataFrame] = []
    data_frame_list_workflows: List[pandas.DataFrame] = []
    data_frame_list_counts: List[Dict[str, Union[str, int]]] = []
    workflows_data_frame = None
    commits_data_frame = None
    counts_data_frame = None
    # extract all of the commits-based CSV files
    with Progress(
        constants.progress.Task_Format,
        BarColumn(),
        constants.progress.Percentage_Format,
        constants.progress.Completed,
        "•",
        TimeElapsedColumn(),
        "elapsed",
        "•",
        TimeRemainingColumn(),
        "remaining",
    ) as progress:
        sorted_directory_glob = sorted(
            csv_directory.glob(constants.filesystem.Csv_Commits_Glob)
        )
        task = progress.add_task(
            "Combine Commit Data", total=len(sorted_directory_glob) + 1
        )
        for csv_file in sorted_directory_glob:
            logger.debug(csv_file)
            csv_file_data_frame = pandas.read_csv(str(csv_file))
            data_frame_list_commits.append(csv_file_data_frame)
            progress.update(task, advance=1)
        commits_data_frame = combine_data_frames(data_frame_list_commits)
        progress.update(task, advance=1)
    logger.debug(len(data_frame_list_commits))
    # extract all of the workflow-based CSV files
    console.print()
    with Progress(
        constants.progress.Task_Format,
        BarColumn(),
        constants.progress.Percentage_Format,
        constants.progress.Completed,
        "•",
        TimeElapsedColumn(),
        "elapsed",
        "•",
        TimeRemainingColumn(),
        "remaining",
    ) as progress:
        sorted_directory_glob = sorted(
            csv_directory.glob(constants.filesystem.Csv_Workflows_Glob)
        )
        task = progress.add_task(
            "Combine Workflow Data", total=len(sorted_directory_glob) + 1
        )
        for csv_file in sorted(
            csv_directory.glob(constants.filesystem.Csv_Workflows_Glob)
        ):
            logger.debug(csv_file)
            csv_file_data_frame = pandas.read_csv(str(csv_file))
            workflow_count_dictionary = create_counts_dictionary(csv_file_data_frame)
            if len(workflow_count_dictionary) != 0:
                data_frame_list_counts.append(workflow_count_dictionary)
            data_frame_list_workflows.append(csv_file_data_frame)
            progress.update(task, advance=1)
        workflows_data_frame = combine_data_frames(data_frame_list_workflows)
        counts_data_frame = pandas.DataFrame(data_frame_list_counts)
        progress.update(task, advance=1)
    logger.debug(len(data_frame_list_workflows))
    console.print()
    return (
        counts_data_frame,
        commits_data_frame,
        workflows_data_frame,
    )


def create_counts_dictionary(
    workflows_data_frame: pandas.DataFrame,
) -> Dict[str, Union[str, int]]:
    """Create a counts dictionary based on attributes and size of workflow data."""
    logger = logging.getLogger(constants.logging.Rich)
    # create an empty dictionary to populate as long as this project has
    # workflows that were recorded by GitHub
    counts_dictionary: Dict[str, Union[str, int]] = {}
    # extract the number of rows in the DataFrame, which corresponds
    # to the number of workflow builds run in GitHub Actions
    number_rows = len(workflows_data_frame)
    # if the project has some rows then there are attributes that we can
    # extract and store in the dictionary that this function returns
    if number_rows != 0:
        counts_dictionary[constants.workflow.Workflow_Build_Count] = number_rows
        counts_dictionary[constants.workflow.Organization] = extract_data(
            workflows_data_frame, constants.workflow.Organization
        )
        counts_dictionary[constants.workflow.Repo] = extract_data(
            workflows_data_frame, constants.workflow.Repo
        )
        counts_dictionary[constants.workflow.Repo_Url] = extract_data(
            workflows_data_frame, constants.workflow.Repo_Url
        )
        counts_dictionary[constants.workflow.Actions_Url] = extract_data(
            workflows_data_frame, constants.workflow.Actions_Url
        )
        counts_dictionary[constants.workflow.Actions_Url] = extract_data(
            workflows_data_frame, constants.workflow.Actions_Url
        )
        logger.debug(counts_dictionary)
    return counts_dictionary


def extract_data(workflows_data_frame: pandas.DataFrame, attribute: str) -> str:
    """Extract a specific attribute from a data frame if it exists."""
    if attribute in workflows_data_frame:
        return workflows_data_frame[attribute].unique().tolist()[0]  # type: ignore
    return constants.markers.Empty


def combine_data_frames(data_frame_list: List[pandas.DataFrame]) -> pandas.DataFrame:
    """Combine all of the data frames in the list to a single data frame."""
    # concatenate together all of the data frames in the list into a
    # single data frame, useful for summarization or saving to file system
    return pandas.concat(data_frame_list)
