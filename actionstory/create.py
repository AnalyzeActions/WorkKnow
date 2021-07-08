"""Create content from containers and strings."""

import logging

from actionstory import constants


def create_github_api_url(organization: str, repo: str) -> str:
    """Create a valid GitHub API URL out of the organization and repo name."""
    # Example:
    # https://api.github.com/repos/gkapfham/meSMSage/actions/runs
    logger = logging.getLogger(constants.logging.Rich)
    github_api_url = (
        constants.github.Https
        + constants.github.Api
        + organization
        + constants.github.Separator
        + repo
        + constants.github.Separator
        + constants.github.Actions
    )
    logger.debug("Created the GitHub API URL: " + github_api_url)
    return github_api_url
