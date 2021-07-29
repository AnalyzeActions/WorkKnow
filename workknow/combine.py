"""Summarize data in CSV files."""

import logging

from pathlib import Path

from typing import List
from typing import Tuple

import pandas

from workknow import constants


def summarize_files_in_directory(csv_directory: Path) -> Tuple[List[pandas.DataFrame], List[pandas.DataFrame]]:
    """Summarize all of the CSV files inside of a directory."""
    logger = logging.getLogger(constants.logging.Rich)
    data_frame_list_commits: List[pandas.DataFrame] = []
    data_frame_list_workflows: List[pandas.DataFrame] = []
    # extract all of the commits-based CSV files
    for csv_file in sorted(csv_directory.glob(constants.filesystem.Csv_Commits_Glob)):
        logger.debug(csv_file)
        csv_file_data_frame = pandas.read_csv(str(csv_file))
        data_frame_list_commits.append(csv_file_data_frame)
    logger.debug(len(data_frame_list_commits))
    # extract all of the workflow-based CSV files
    for csv_file in sorted(csv_directory.glob(constants.filesystem.Csv_Workflows_Glob)):
        logger.debug(csv_file)
        csv_file_data_frame = pandas.read_csv(str(csv_file))
        data_frame_list_workflows.append(csv_file_data_frame)
    logger.debug(len(data_frame_list_workflows))
    return (data_frame_list_commits, data_frame_list_workflows)


def summarize_data_frames(data_frame_list: List[pandas.DataFrame]) -> pandas.DataFrame:
    """Summarize all of the data frames in the list to a single data frame."""
    return pandas.concat(data_frame_list)
