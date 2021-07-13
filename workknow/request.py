"""Use the GitHub REST API to access information about GitHub Action Workflows."""

import datetime
import logging
import os
import time

from typing import Dict
from typing import List

from rich.console import Console

import pytz
import requests

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
    return json_responses[constants.github.Workflow_Runs]


def get_rate_limit_details():
    """Request a JSON response from the GitHub API about rate limits."""
    # initialize the logging subsystem
    logger = logging.getLogger(constants.logging.Rich)
    # define the URL needed to access rate limiting data
    github_api_url = constants.rate.Rate_Limit_Url
    # access the person's GitHub personal access token so that
    # the use of the tool is not rapidly rate limited
    github_authentication = (constants.github.User, get_github_personal_access_token())
    # use requests to access the GitHub API with:
    # --> provided GitHub URL that accesses a project's GitHub Actions log
    # --> the parameters that currently specify the page limit and will specify the page
    # --> the GitHub authentication information with the personal access token
    response = requests.get(github_api_url, auth=github_authentication)
    response_json_dict = response.json()
    logger.debug(response_json_dict)
    return response_json_dict[constants.rate.Resources][constants.rate.Core]


def utc_to_time(naive, timezone):
    """Convert a UTC time zone that is naive to a locally situation timezone."""
    return naive.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(timezone))


def get_rate_limit_wait_time(rate_limit_dict: Dict[str, int]) -> int:
    """Determine the amount of time needed for waiting because of rate limit."""
    # initialize the logging subsystem
    console = Console()
    logger = logging.getLogger(constants.logging.Rich)
    # extract reset time from the response from the GitHub API
    reset_time_in_utc_epoch_seconds = rate_limit_dict[constants.rate.Reset]
    # extract the local time zone to help with display of debugging information
    local_time_zone = os.getenv(constants.environment.Timezone)
    current_timezone = pytz.timezone(local_time_zone)
    # convert the epoch seconds to a UTC-zoned datetime
    reset_datetime = datetime.datetime.utcfromtimestamp(reset_time_in_utc_epoch_seconds)
    # convert the UTC-zoned datetime to a local-zone datetime
    reset_datetime_local = utc_to_time(reset_datetime, current_timezone.zone)
    # display debugging information
    logger.debug(reset_time_in_utc_epoch_seconds)
    logger.debug(reset_datetime)
    logger.debug(reset_datetime_local)
    # calculate the number of seconds needed to sleep until the reset happens for GitHub's API
    current_time = datetime.datetime.now(datetime.timezone.utc)
    current_time_utc_timestamp = current_time.timestamp()
    sleep_time_seconds = reset_time_in_utc_epoch_seconds - current_time_utc_timestamp
    logger.debug(current_time_utc_timestamp)
    logger.debug(sleep_time_seconds)
    # the program is in danger of being rate limited, which will cause a crash, and
    # thus it is better to sleep for the remainder of the period until the reset
    if rate_limit_dict[constants.rate.Remaining] < constants.rate.Threshold:
        logger.debug(sleep_time_seconds)
        console.print(f":sleeping_face: Sleeping for {sleep_time_seconds} to wait until the GitHub API resets the rate limits")
        time.sleep(sleep_time_seconds + constants.rate.Extra_Seconds)


def request_json_from_github(github_api_url: str) -> List:
    """Request the JSON response from the GitHub API."""
    # initialize the logging subsystem
    logger = logging.getLogger(constants.logging.Rich)
    # access the person's GitHub personal access token so that
    # the use of the tool is not rapidly rate limited
    github_authentication = (constants.github.User, get_github_personal_access_token())
    # request the maximum of number of entries per page
    github_params = {constants.github.Per_Page: constants.github.Per_Page_Maximum}
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
    page = constants.github.Page_Start
    # continue to extract data from the pages as long as the "next" field is evident
    while constants.github.Next in response.links.keys():
        # update the "page" variable in the URL to go to the next page
        # otherwise, make sure to use all of the same parameters as the first request
        github_params[constants.github.Page] = str(page)
        response = requests.get(
            github_api_url, params=github_params, auth=github_authentication
        )
        logger.debug(response.headers)
        # again extract the specific workflow runs list and append it to running response details
        json_responses.append(get_workflow_runs(response.json()))
        # go to the next page in the pagination results list
        page = page + 1
        # check if the program is about to exceed GitHub's rate limit and then
        # sleep the program until the reset time has elapsed
        rate_limit_dict = get_rate_limit_details()
        get_rate_limit_wait_time(rate_limit_dict)
    # return the list of workflow runs dictionaries
    return json_responses
