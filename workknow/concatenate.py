"""Combine data in CSV files in provided directories and create Pandas DataFrames."""

import logging

from pathlib import Path

from typing import List
from typing import Tuple

import pandas

from rich.progress import BarColumn
from rich.progress import Progress
from rich.progress import TimeRemainingColumn
from rich.progress import TimeElapsedColumn

from workknow import configure
from workknow import constants


def summarize_files_in_directory(
    csv_directory: Path,
) -> Tuple[pandas.DataFrame, pandas.DataFrame]:
    """Summarize all of the CSV files inside of a directory."""
    logger = logging.getLogger(constants.logging.Rich)
    console = configure.setup_console()
    data_frame_list_commits: List[pandas.DataFrame] = []
    data_frame_list_workflows: List[pandas.DataFrame] = []
    commits_data_frame = None
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
        commits_data_frame = pandas.concat(data_frame_list_commits)
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
            data_frame_list_workflows.append(csv_file_data_frame)
            progress.update(task, advance=1)
        workflows_data_frame = pandas.concat(data_frame_list_workflows)
        progress.update(task, advance=1)
    logger.debug(len(data_frame_list_workflows))
    console.print()
    return (
        commits_data_frame,
        workflows_data_frame,
    )


def summarize_data_frames(data_frame_list: List[pandas.DataFrame]) -> pandas.DataFrame:
    """Summarize all of the data frames in the list to a single data frame."""
    # concatenate together all of the data frames in the list into a
    # single data frame, useful for summarization or saving to file system
    return pandas.concat(data_frame_list)
