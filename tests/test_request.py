"""Tests for the request module."""

import responses

from workknow import configure
from workknow import debug
from workknow import request


@responses.activate
def test_failure_backoff_one_retry_mocked():
    """Check that a mocked request to an API fails and handles correctly."""
    # configure the system so that it does not produce debugging output
    debug_level = debug.DebugLevel.ERROR
    console, _ = configure.setup(debug_level)
    # define a URL that can be interacted with in a mocked fashion; importantly,
    # this test case is using responses and thus there is no actual interaction
    # with the GitHub API and no network transmission at all
    github_api_url = "https://api.github.com/repos/home-assistant/core/actions/runs"
    # define the response that the mocked API will return for al interactions
    responses.add(
        responses.GET,
        github_api_url,
        json={"message": "server error"},
        status=502,
    )
    # attempt to download the JSON data from the mocked GitHub API; since this
    # will always result in failure this will cause the exponential back-off
    # and retry mechanism to start working until the maximum number of retries
    (
        valid,
        total_retry_count,
        total_retry_time,
        json_responses_list,
    ) = request.request_json_from_github(github_api_url, console, 1)
    assert valid is False
    assert json_responses_list == []
    assert total_retry_count == 1
    assert total_retry_time == 1


@responses.activate
def test_failure_backoff_three_retries_mocked():
    """Check that a mocked request to an API fails and handles correctly."""
    # configure the system so that it does not produce debugging output
    debug_level = debug.DebugLevel.ERROR
    console, _ = configure.setup(debug_level)
    # define a URL that can be interacted with in a mocked fashion; importantly,
    # this test case is using responses and thus there is no actual interaction
    # with the GitHub API and no network transmission at all
    github_api_url = "https://api.github.com/repos/home-assistant/core/actions/runs"
    # define the response that the mocked API will return for al interactions
    responses.add(
        responses.GET,
        github_api_url,
        json={"message": "server error"},
        status=502,
    )
    # attempt to download the JSON data from the mocked GitHub API; since this
    # will always result in failure this will cause the exponential back-off
    # and retry mechanism to start working until the maximum number of retries
    (
        valid,
        total_retry_count,
        total_retry_time,
        json_responses_list,
    ) = request.request_json_from_github(github_api_url, console, 3)
    assert valid is False
    assert json_responses_list == []
    assert total_retry_count == 3
    assert total_retry_time == (1 + 2 + 4)
