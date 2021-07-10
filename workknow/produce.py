"""Create content from containers and strings."""

import logging

from typing import Any
from typing import Dict
from typing import List

import pandas

from workknow import constants


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


def count_individual_builds(json_responses: List[Dict[Any, Any]]) -> int:
    """Count the number of lists inside of the nested list."""
    running_build_total = 0
    # iterate through each of the JSON responses in the list and
    # count the number of dicts inside of the list. Note that each
    # of these dicts corresponds to one of the build entries.
    for internal_json_responses in json_responses:
        running_build_total = running_build_total + len(internal_json_responses)
    # return the running total of builds
    return running_build_total


def create_workflows_dataframe(
    workflows_dictionary_list: List[Dict[Any, Any]]
) -> pandas.DataFrame:
    """Create a dictionary of all of the relevant workflow data."""
    # create a tuple of the key names that we want to retain from
    # those keys that are inside of all those in a dictionary (row) of data
    subset_key_names = {
        "id",
        "name",
        "head_sha",
        "created_at",
        "updated_at",
        "event",
        "status",
        "conclusion",
        "jobs_url",
    }
    # create an empty list that will store dictionaries to be made into
    # rows of a Pandas DataFrame. This approach avoids the need to incrementally
    # add rows to a Pandas DataFrame, which is known to be inefficient.
    total_workflow_list = []
    # iterate through the outer list that contains a separate list for each
    # of the separate pages returned from the GitHub API
    for current_workflow_dictionary_inner_list in workflows_dictionary_list:
        # iterate through the inner list which contains a dictionary for each
        # "row" in the JSON file that was returned from the GitHub API
        for current_workflow_dictionary in current_workflow_dictionary_inner_list:
            # only keep those key-value pairs that are for keys in subset_key_names
            chosen_keys_values = {
                key: value
                for key, value in current_workflow_dictionary.items()
                if key in subset_key_names
            }
            # add the list of chosen key-value pairs to the list of workflow details
            total_workflow_list.append(chosen_keys_values)
    # create a Pandas DataFrame from the list of dictionaries
    total_workflow_dataframe = pandas.DataFrame(total_workflow_list)
    return total_workflow_dataframe
