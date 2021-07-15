"""Load and save files."""

import logging
import zipfile

from pathlib import Path

from typing import List

import pandas

from workknow import configure
from workknow import constants


def read_csv_file(csv_data_file: Path) -> pandas.DataFrame:
    """Read a CSV file and return it as a Pandas DataFrame."""
    # create an empty DataFrame for the situation in which
    # the program attempts to read a CSV file that does not
    # have any data in it and thus an exception is thrown
    data_frame_csv = pandas.DataFrame()
    try:
        # try to read a tabular data set set stored in a CSV file
        csv_file_data_frame = pandas.read_csv(str(csv_data_file))
        # there was no exception and thus it is fine to return the DataFrame
        return pandas.DataFrame(csv_file_data_frame)
    # the CSV file was empty and thus we must return an empty DataFrame
    except pandas.errors.EmptyDataError:
        return data_frame_csv


def create_directory(directory: Path) -> None:
    """Create a directory if it does not exist and don't fail if it does."""
    # create the complete file path, making all parent directories
    # if needed and not failing if the directory already exists
    console = configure.setup_console()
    # attempt to create the directory
    try:
        directory.mkdir(parents=True, exist_ok=True)
    # permission errors developed, this means that it is not possible to
    # create the directory and thus the program cannot save its results;
    # display diagnostic information about what exception happened
    except PermissionError:
        console.print(":grimacing_face: Unable to save in the provided directory")
        console.print()


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


def create_results_zip_file_list(results_directory: Path) -> List[str]:
    """Create a list of the .csv files in the provided results directory."""
    results_files_generator = results_directory.glob("*.csv")
    results_file_list = []
    for results_file in results_files_generator:
        results_file_list.append(str(results_file))
    return results_file_list


def create_results_zip_file(
    results_directory: Path, results_file_list: List[str]
) -> None:
    """Save a .zip file in the results directory of all the provided .csv files found in the results directory."""
    # create a context for the .zip file in the variable results_zip_file
    with zipfile.ZipFile(
        str(results_directory)
        + constants.filesystem.Slash
        + constants.filesystem.All
        + constants.filesystem.Dash
        + constants.workknow.Name
        + constants.filesystem.Dash
        + constants.filesystem.Results
        + constants.filesystem.Zip_Extension,
        "w",
    ) as results_zip_file:
        # iterate through each of the file names in the list of file names
        for results_file_name in results_file_list:
            # create a Pathlib-based Path out of the results_file_name
            # since that will allow for the extraction of only the name
            # of the file and thus ensure that the .zip file does not
            # contain inside of it the full directory structure associated
            # with where the results files are currently located
            pathlib_path_file = Path(results_file_name)
            # review of the arguments to write:
            # --> Parameter 1: the name of the file as found on current file system
            # --> Parameter 2: the name of the file as it will be stored in the .zip file
            results_zip_file.write(results_file_name, pathlib_path_file.name)
