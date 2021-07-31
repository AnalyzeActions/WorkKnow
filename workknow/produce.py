"""Create content from containers and strings."""

import logging

from typing import Any
from typing import Dict
from typing import List
from typing import Set
from typing import Tuple
from typing import Union

from giturlparse import parse  # type: ignore

import pandas

from workknow import constants


def parse_github_url(github_url: str) -> Tuple[Union[str, None], Union[str, None]]:
    """Parse a GitHub URL using the giturlparse package returning names of organization and repository."""
    # the provided github_url is valid and can be parsed
    if parse(github_url).valid:
        # parse the parse-able github_url
        github_url_parse = parse(github_url)
        # extract the owner (i.e., organization) and repo fields
        # and return them both in a tuple
        organization = github_url_parse.owner  # type: ignore
        repository = github_url_parse.repo  # type: ignore
        return (organization, repository)
    # the provided github_url was not parse-able so return None
    return (None, None)


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


def create_subsetted_list_dict(
    organization: str,
    repo: str,
    repo_url: str,
    subset_key_names: Set,
    workflows_dictionary_list: List[Dict[Any, Any]],
) -> List[Dict[Any, Any]]:
    """Create a list of dictionaries of all of the relevant workflow data."""
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
            # to ensure that the data set is self contained (and also to ensure that
            # records for multiple projects can be stored in the same "All" DataFrame),
            # include the organization name, repository name, and full repository URL
            # inside of the dictionary before it is stored inside of the list
            chosen_keys_values[constants.workflow.Organization] = organization
            chosen_keys_values[constants.workflow.Repo] = repo
            chosen_keys_values[constants.workflow.Repo_Url] = repo_url
            # add the list of chosen key-value pairs to the list of workflow details
            total_workflow_list.append(chosen_keys_values)
    # return the list of dicts so that calling method can analyze it further
    # or create a Pandas data frame out of it
    return total_workflow_list


def create_workflows_dataframe(
    organization: str,
    repo: str,
    repo_url: str,
    workflows_dictionary_list: List[Dict[Any, Any]],
) -> pandas.DataFrame:
    """Create a DataFrame of all of the relevant workflow data."""
    # create a tuple of the key names that we want to retain from
    # those keys that are inside of all those in a dictionary (row) of data
    subset_key_names = {
        constants.workflow.Id,
        constants.workflow.Name,
        constants.workflow.Head_Sha,
        constants.workflow.Created_At,
        constants.workflow.Updated_At,
        constants.workflow.Event,
        constants.workflow.Status,
        constants.workflow.Conclusion,
        constants.workflow.Jobs_Url,
    }
    total_workflow_list = create_subsetted_list_dict(
        organization, repo, repo_url, subset_key_names, workflows_dictionary_list
    )
    total_workflow_dataframe = pandas.DataFrame(total_workflow_list)
    return total_workflow_dataframe


def create_commits_dataframe(
    organization: str,
    repo: str,
    repo_url: str,
    workflows_dictionary_list: List[Dict[Any, Any]],
) -> pandas.DataFrame:
    """Create a DataFrame of all the relevant commit message data."""
    # create a tuple of the key names that we want to retain from
    # those keys that are inside of all those in a dictionary (row) of data
    subset_key_names = {
        constants.workflow.Head_Commit,
    }
    # create a subsetted list given the key names
    commits_list = create_subsetted_list_dict(
        organization, repo, repo_url, subset_key_names, workflows_dictionary_list
    )
    # Since the commits list of dictionaries contains dictionaries that are
    # nested in their structure, they must be normalized and then stored
    # inside of a Pandas DataFrame. That results in variables with longer,
    # hyphenated names that arise due to the flattening of nested dictionaries
    total_commits_dataframe = pandas.json_normalize(
        commits_list, sep=constants.markers.Underscore
    )
    return total_commits_dataframe


def create_workflow_record_count_dictionary(
    organization: str,
    repo: str,
    repo_url: str,
    github_api_url: str,
    workflows_dictionary_list: List[Dict[Any, Any]],
) -> Dict[str, Union[str, int]]:
    """Create a dictionary of all the counts of records returned for a GitHub project's workflows."""
    # create the empty dictionary that will store the relevant meta-data and the record count
    workflow_count_dictionary: Dict[str, Union[str, int]] = {}
    # count the individual builds for a given GitHub repository's workflows
    workflows_count_for_repo = count_individual_builds(workflows_dictionary_list)
    # store all of the meta-data about this project:
    # --> GitHub organization name
    # --> GitHub repository name
    # --> GitHub repository URL
    # --> GitHub API URL used to access workflow data
    workflow_count_dictionary[constants.workflow.Organization] = str(organization)
    workflow_count_dictionary[constants.workflow.Repo] = str(repo)
    workflow_count_dictionary[constants.workflow.Repo_Url] = str(repo_url)
    workflow_count_dictionary[constants.workflow.Actions_Url] = str(github_api_url)
    # store the count of all the workflow records for this repository
    workflow_count_dictionary[
        constants.workflow.Workflow_Build_Count
    ] = workflows_count_for_repo
    return workflow_count_dictionary


def extract_repo_urls_list(repos_dataframe: pandas.DataFrame) -> List[Union[str, Any]]:
    """Extract a list of urls from the provided Pandas DataFrame."""
    # create an empty list of URLs to return if the DataFrame of repositories
    # does not have the correct "url" column name or is otherwise malformed
    url_column_list = []
    # confirm that the provided DataFrame contains the required column called "url"
    if constants.data.Url in repos_dataframe.columns:
        # extract the data in the "url" column from the entire DataFrame
        url_column_series = repos_dataframe[constants.data.Url]
        # convert the series arising from the "url" column to a list
        if url_column_series is not None:
            url_column_list = url_column_series.tolist()
    return list(url_column_list)
