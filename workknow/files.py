"""Load and save files."""

import logging

from pathlib import Path

import pandas

from workknow import constants


def read_csv_file(csv_data_file: Path) -> pandas.DataFrame:
    """Read a CSV file and return it as a Pandas DataFrame."""
    # read a tabular data set set stored in a CSV file
    csv_file_data_frame = pandas.read_csv(str(csv_data_file))
    return csv_file_data_frame


def create_directory(directory: Path) -> None:
    """Create a directory if it does not exist and don't fail if it does."""
    # create the complete file path, making all parent directories
    # if needed and not failing if the directory already exists
    directory.mkdir(parents=True, exist_ok=True)


def confirm_valid_file(file: Path) -> bool:
    """Confirm that the provided file is a valid path."""
    # determine if the file is not None and if it is a file
    if file is not None:
        if file.is_file():
            return True
    return False


def confirm_valid_directory(directory: Path) -> bool:
    """Confirm that the provided directory is a valid path."""
    # attempt to create the directory first if it does not already exist
    if directory is not None:
        create_directory(directory)
        if directory.is_dir():
            return True
    return False


def save_dataframe_all(
    results_dir: Path,
    label: str,
    repo_data: pandas.DataFrame,
) -> None:
    """Save the provided DataFrame in a file in the results_dir with a label for all data sets."""
    # create the complete file path, making all parent directories
    # if needed and not failing if the directory already exists
    create_directory(results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)
    # create the directory given the provided input details
    file_name = (
        constants.filesystem.All
        + constants.filesystem.Dash
        + label
        + constants.filesystem.Csv_Extension
    )
    # log the name of the file and the results directory
    logger = logging.getLogger(constants.logging.Rich)
    logger.debug(results_dir)
    logger.debug(file_name)
    # construct the complete file path including (in order):
    # --> the fully qualified path for the results directory
    # --> the full name of the file storing the data
    complete_file_path = results_dir / file_name
    # resolve the complete file path to get its absolute name
    resolved_complete_file_path = complete_file_path.resolve()
    # convert the pathlib Path object to a string and then use
    # Pandas to save the file to the textualized path as a CSV file
    repo_data.to_csv(str(resolved_complete_file_path))


def save_dataframe(
    results_dir: Path,
    organization: str,
    repository: str,
    label: str,
    repo_data: pandas.DataFrame,
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
        + constants.filesystem.Dash
        + label
        + constants.filesystem.Csv_Extension
    )
    # log the name of the file and the results directory
    logger = logging.getLogger(constants.logging.Rich)
    logger.debug(results_dir)
    logger.debug(file_name)
    # construct the complete file path including (in order):
    # --> the fully qualified path for the results directory
    # --> the full name of the file storing the data
    complete_file_path = results_dir / file_name
    # resolve the complete file path to get its absolute name
    resolved_complete_file_path = complete_file_path.resolve()
    # convert the pathlib Path object to a string and then use
    # Pandas to save the file to the textualized path as a CSV file
    repo_data.to_csv(str(resolved_complete_file_path))
