"""Load and save files."""

import logging
import zipfile

from pathlib import Path
from glob import glob

from typing import List
from typing import Tuple

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


def read_csv_data_files(
    csv_data_file_directory: Path,
) -> Tuple[pandas.DataFrame, pandas.DataFrame, pandas.DataFrame]:
    """Read in the three main results files and return as Pandas DataFrames."""
    # create the All-Counts.csv file as a pathlib Path object
    csv_data_file_all_counts = csv_data_file_directory / (
        constants.filesystem.All
        + constants.filesystem.Dash
        + constants.filesystem.Counts
        + constants.filesystem.Csv_Extension
    )
    # read the All-Counts.csv file from the data file directory
    csv_data_file_all_counts_df = read_csv_file(csv_data_file_all_counts)
    # create the All-Commits.csv file as a pathlib Path object
    csv_data_file_all_commits = csv_data_file_directory / (
        constants.filesystem.All
        + constants.filesystem.Dash
        + constants.filesystem.Commits
        + constants.filesystem.Csv_Extension
    )
    # read the All-Commits.csv file from the data file directory
    csv_data_file_all_commits_df = read_csv_file(csv_data_file_all_commits)
    # create the All-Workflows.csv file as a pathlib Path object
    csv_data_file_all_workflows = csv_data_file_directory / (
        constants.filesystem.All
        + constants.filesystem.Dash
        + constants.filesystem.Workflows
        + constants.filesystem.Csv_Extension
    )
    # read the All-Commits.csv file from the data file directory
    csv_data_file_all_workflows_df = read_csv_file(csv_data_file_all_workflows)
    return (csv_data_file_all_counts_df, csv_data_file_all_commits_df, csv_data_file_all_workflows_df)


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


def create_paths(*args, file=constants.markers.Nothing, home):
    """Create a generator of Path objects for a glob with varying sub-path count."""
    # attempt to create the path that could contain:
    # --> a glob (e.g., *.py) or
    # --> a single file (e.g., hello.py)
    # Pathlib does not support globs of absolute directories, so use glob
    # to create a list of all files matched by the glob
    file_or_glob_path = create_path(*args, file=file, home=home)
    home_directory_globbed = [Path(p) for p in glob(str(file_or_glob_path))]
    # return this list of Path objects resulting from glob application
    return home_directory_globbed


def create_path(*args, file=constants.markers.Nothing, home):
    """Create a Path object for a file with varying sub-path count."""
    # create the Path for the home
    home_path = Path(home)
    # create the Path for the given file
    given_file_path = Path(file)
    final_path = home_path
    # Create a containing directory of sub-directories for the file.
    # Each of these paths will be a path between the home and the
    # specified file. None of these paths need their anchor, though,
    # which is given like "C:\" on Windows and "/" otherwise.
    # pylint: disable=old-division
    for containing_path in args:
        nested_path = Path(containing_path)
        final_path = final_path / nested_path.relative_to(nested_path.anchor)
    # add the file at the end of the constructed file path
    final_path = final_path / given_file_path
    return final_path
