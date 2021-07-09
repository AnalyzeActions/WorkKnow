"""Use Python HTTPx to Access the GitHub API."""

import logging
import os

from typing import Dict
from typing import List

import requests
from dotenv import load_dotenv

from actionstory import constants

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
    github_personal_access_token = os.getenv(constants.environment.Github)
    return github_personal_access_token


def request_json_from_github(github_api_url: str) -> Dict[str, Dict[str, List[str]]]:
    """Request the JSON response from the GitHub API."""
    logger = logging.getLogger(constants.logging.Rich)
    github_authentication = ('user', get_github_personal_access_token())
    github_params = {"per_page": "30"}
    response = requests.get(github_api_url, auth=github_authentication)
    json_responses = response.json()
    logger.debug(response.headers)
    page = 2
    while "next" in response.links.keys():
        github_params = {"page": str(page)}
        response = requests.get(github_api_url, params=github_params, auth=github_authentication)
        logger.debug(response.headers)
        json_responses.update(response.json())
        page = page + 1
    return json_responses
