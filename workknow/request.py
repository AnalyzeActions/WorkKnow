"""Use the GitHub REST API to access information about GitHub Action Workflows."""

import logging
import os

from typing import List

import requests
from dotenv import load_dotenv

from workknow import constants

# Sample of the JSON file returned by the request:

# {
# │   'total_count': 149,
# │   'workflow_runs': [
# │   │   {'id': 161802486, 'name': 'build', 'node_id': 'MDExOldvcmtmbG93UnVuMTYxODAyNDg2', 'head_branch': 'commit_message_check', ... +23},
# │   │   {'id': 160433969, 'name': 'build', 'node_id': 'MDExOldvcmtmbG93UnVuMTYwNDMzOTY5', 'head_branch': 'commit_message_check', ... +23},
# │   │   {'id': 160372604, 'name': 'build', 'node_id': 'MDExOldvcmtmbG93UnVuMTYwMzcyNjA0', 'head_branch': 'commit_message_check', ... +23},
# │   │   {'id': 160358243, 'name': 'build', 'node_id': 'MDExOldvcmtmbG93UnVuMTYwMzU4MjQz', 'head_branch': 'commit_message_check', ... +23},
# │   │   ... +25
# │   ]
# }

# use the python-dotenv package to load the .env file
# (created by the user) that will contain the GitHub
# personal access token that allows for API interactions
# before the rate limit will be enforced
# Reference
# https://docs.github.com/en/rest/overview/resources-in-the-rest-api#rate-limiting
load_dotenv()


def get_github_personal_access_token():
    """Retrieve the GitHub personal access token from the environment."""
    # extract the GITHUB_ACCESS_TOKEN environment variable; note that this
    # only works because of the fact that load_dotenv was previously called
    github_personal_access_token = os.getenv(constants.environment.Github)
    return github_personal_access_token


def get_workflow_runs(json_responses):
    """Get the list of workflow run information for a JSON-deri ed dictionary."""
    # this dictionary has a key called "workflow_runs" that has as its value a
    # list of dictionaries, one for each run inside of GitHub Actions. This
    # will return the list so that it can be stored and analyzed.
    return json_responses["workflow_runs"]


def request_json_from_github(github_api_url: str) -> List:
    """Request the JSON response from the GitHub API."""
    # initialize the logging subsystem
    logger = logging.getLogger(constants.logging.Rich)
    # access the person's GitHub personal access token so that
    # the use of the tool is not rapidly rate limited
    github_authentication = ("user", get_github_personal_access_token())
    # request the maximum of 100 entries per page
    github_params = {"per_page": "100"}
    # use requests to access the GitHub API with:
    # --> provided GitHub URL that accesses a project's GitHub Actions log
    # --> the parameters that currently specify the page limit and will specify the page
    # --> the GitHub authentication information with the personal access token
    response = requests.get(
        github_api_url, params=github_params, auth=github_authentication
    )
    # create an empty list that can store all of the JSON responses for workflow runs
    json_responses = []
    # extract the JSON document (it is a dict) and then extract from that the workflow runs list
    # finally, append the list of workflow runs to the running list of response details
    json_responses.append(get_workflow_runs(response.json()))
    logger.debug(response.headers)
    # pagination in GitHub Actions is 1-indexed (i.e., the first index is 1)
    # and thus the next page that we will need to extract (if needed) is 2
    page = 2
    # continue to extract data from the pages as long as the "next" field is evident
    while "next" in response.links.keys():
        # update the "page" variable in the URL to go to the next page
        # otherwise, make sure to use all of the same parameters as the first request
        github_params["page"] = str(page)
        response = requests.get(
            github_api_url, params=github_params, auth=github_authentication
        )
        logger.debug(response.headers)
        # again extract the specific workflow runs list and append it to running response details
        json_responses.append(get_workflow_runs(response.json()))
        # go to the next page in the pagination results list
        page = page + 1
    # return the list of workflow runs dictionaries
    return json_responses
