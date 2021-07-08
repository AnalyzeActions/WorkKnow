"""Use Python HTTPx to Access the GitHub API."""

import logging

import requests

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


def request_json_from_github(github_api_url: str) -> str:
    """Request the JSON response from the GitHub API."""
    github_params = {"per_page": "100"}
    response = requests.get(github_api_url, headers=github_params)
    json_response = response.json()
    logger = logging.getLogger(constants.logging.Rich)
    logger.debug(response.headers)
    while "next" in response.links.keys():
        response = requests.get(response.links["next"]["url"])
        json_response.update(response.json())
    return json_response
