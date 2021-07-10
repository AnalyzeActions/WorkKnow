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
    logger = logging.getLogger(constants.logging.Rich)
    file_name = organization + "-" + repository + ".csv"
    logger.debug(results_dir)
    complete_file_path = results_dir / file_name
    resolved_complete_file_path = complete_file_path.resolve()
    results_dir.mkdir(parents=True, exist_ok=True)
    repo_data.to_csv(str(resolved_complete_file_path))
