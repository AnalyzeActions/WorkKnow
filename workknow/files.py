"""Load and save files."""

import logging
from pathlib import Path

import pandas

from workknow import constants


def save_dataframe(
    results_dir: Path, organization: str, repository: str, repo_data: pandas.DataFrame
) -> None:
    """Save the provided DataFrame in a file connected to organization and repo in the results_dir."""
    # create the directory given the provided input details
    file_name = organization + "-" + repository + ".csv"
    # log the name of the file and the results directory
    logger = logging.getLogger(constants.logging.Rich)
    logger.debug(results_dir)
    logger.debug(file_name)
    # construct the complete file path
    complete_file_path = results_dir / file_name
    # resolve the complete file path to get its absolute name
    resolved_complete_file_path = complete_file_path.resolve()
    # create the complete file path, making all parent directories
    # if needed and not failing if the directory already exists
    results_dir.mkdir(parents=True, exist_ok=True)
    # convert the pathlib Path object to a string and then use
    # Pandas to save the file to the textualized path as a CSV file
    repo_data.to_csv(str(resolved_complete_file_path))
