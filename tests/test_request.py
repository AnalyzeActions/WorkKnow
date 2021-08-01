"""Tests for the request module."""

import responses

from workknow import configure
from workknow import debug
from workknow import request


@responses.activate
def test_simple():
    """Check that a mocked request to an API fails and handles correctly."""
    debug_level = debug.DebugLevel.ERROR
    console, _ = configure.setup(debug_level)
    github_api_url = "https://api.github.com/repos/home-assistant/core/actions/runs"
    responses.add(
        responses.GET,
        github_api_url,
        json={"message": "server error"},
        status=502,
    )
    (valid, json_responses_list) = request.request_json_from_github(github_api_url, console, 3)
    assert valid is False
    assert json_responses_list == []
