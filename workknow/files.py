"""Load and save files."""

import logging
from pathlib import Path

import pandas

from workknow import constants


def create_directory(directory: Path) -> None:
    """Create a directory if it does not exist and don't fail if it does."""
    # create the complete file path, making all parent directories
    # if needed and not failing if the directory already exists
    directory.mkdir(parents=True, exist_ok=True)


def confirm_valid_directory(directory: Path) -> bool:
    """Confirm that the provided results directory is a valid path."""
    # attempt to create the directory first if it does not already exist
    if directory is not None:
        create_directory(directory)
        if directory.is_dir():
            return True
    return False


def save_dataframe(
    results_dir: Path, organization: str, repository: str, repo_data: pandas.DataFrame
) -> None:
    """Save the provided DataFrame in a file connected to organization and repo in the results_dir."""
    # create the complete file path, making all parent directories
    # if needed and not failing if the directory already exists
    create_directory(results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)
    # create the directory given the provided input details
    file_name = (
        organization
        + constants.filesystem.Dash
        + repository
        + constants.filesystem.Csv_Extension
    )
    # log the name of the file and the results directory
    logger = logging.getLogger(constants.logging.Rich)
    logger.debug(results_dir)
    logger.debug(file_name)
    # construct the complete file path
    complete_file_path = results_dir / file_name
    # resolve the complete file path to get its absolute name
    resolved_complete_file_path = complete_file_path.resolve()
    # convert the pathlib Path object to a string and then use
    # Pandas to save the file to the textualized path as a CSV file
    repo_data.to_csv(str(resolved_complete_file_path))
