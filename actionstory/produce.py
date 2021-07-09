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


def count_individual_builds(json_responses) -> int:
    """Count the number of lists inside of the nested list."""
    running_build_total = 0
    # iterate through each of the JSON responses in the list and
    # count the number of dicts inside of the list. Note that each
    # of these dicts corresponds to one of the build entries.
    for internal_json_responses in json_responses:
        running_build_total = running_build_total + len(internal_json_responses)
    # return the running total of builds
    return running_build_total
