"""Define constants for use in meSMSage."""

import collections
import itertools


def create_constants(name, *args, **kwargs):
    """Create a namedtuple of constants."""
    # the constants are created such that:
    # the name is the name of the namedtuple
    # for *args with "Constant_Name" or **kwargs with Constant_Name = "AnyConstantName"
    # note that this creates a constant that will
    # throw an AttributeError when attempting to redefine
    # the return value from this function is always a new type
    new_constants = collections.namedtuple(name, itertools.chain(args, kwargs.keys()))
    return new_constants(*itertools.chain(args, kwargs.values()))


# define the constants for environment variables
environment = create_constants(
    "environment",
    Github="GITHUB_ACCESS_TOKEN",
)


# define the constants for environment variables
filesystem = create_constants(
    "filesystem",
    Commits="Commits",
    Csv_Extension=".csv",
    Dash="-",
    Workflows="Workflows",
)


# define the constants for accessing GitHub
github = create_constants(
    "github",
    Actions="actions/runs",
    Api="api.github.com/repos/",
    Https="https://",
    Next="next",
    Page="page",
    Page_Start=2,
    Per_Page="per_page",
    Per_Page_Maximum="100",
    Separator="/",
    User="User",
    Workflow_Runs="workflow_runs",
)


# The defined logging levels, in order of increasing severity, are as follows:
#
# DEBUG
# INFO
# WARNING
# ERROR
# CRITICAL

# define the logging constants
logging = create_constants(
    "logging",
    Debug="DEBUG",
    Info="INFO",
    Warning="WARNING",
    Error="ERROR",
    Critical="CRITICAL",
    Default_Logging_Level="ERROR",
    Format="%(message)s",
    Rich="Rich",
)

# define the constants for markers
markers = create_constants(
    "markers",
    Space=" ",
)


# define the constants for workflow
workflow = create_constants(
    "workflow",
    Conclusion="conclusion",
    Created_At="created_at",
    Event="event",
    Head_Commit="head_commit",
    Head_Sha="head_sha",
    Jobs_Url="jobs_url",
    Id="id",
    Name="name",
    Status="status",
    Updated_At="updated_at",
)


# define the constants for workknow
workknow = create_constants(
    "workknow",
    Emoji=":light_bulb:",
    Tagline="WorkKnow: Know Your GitHub Actions Workflows!",
    Https="https://",
    Separator="/",
)
