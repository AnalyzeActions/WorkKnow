"""Use Python HTTPx to Access the GitHub API."""

import logging

import requests

from actionstory import constants


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
