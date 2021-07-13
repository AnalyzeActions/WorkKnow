"""Load and manage the environment variables."""

from logging import Logger
from pathlib import Path

import os

from dotenv import load_dotenv

from workknow import constants


def load_environment(env_file: Path, logger: Logger) -> None:
    """Load the environment using the dotenv package."""
    env_file_name = constants.markers.Nothing
    # the file was specified and it is valid so derive its full name
    if env_file is not None:
        if env_file.is_file():
            # DEBUG: indicate that the .env file on command-line is in use
            logger.debug("Using provided .env file from the command-line")
            # convert the Pathlib Path to a string
            env_file_name = str(env_file)
    # the file name was not specified so construct the default name
    else:
        env_file_name = constants.markers.Nothing.join(
            [os.getcwd(), os.sep, constants.files.Env]
        )
        # DEBUG: indicate the use of the .env file in the current working directory
        logger.debug("Using constructed .env file in current directory")
    # DEBUG: display the constructed name of the .env file
    logger.debug(f"Environment file: {env_file_name}")
    # load the required secure environment for connecting to Google Sheets
    dotenv_load_environment(env_file_name)


def dotenv_load_environment(env_file_name: str = None) -> None:
    """Load the environment using the specified .env file name."""
    # load the environment variables
    # --> no file is specified, so load from environment variables
    if env_file_name is None:
        load_dotenv()
    # --> file is specified, so load from it instead of environment variables
    else:
        load_dotenv(dotenv_path=env_file_name)
