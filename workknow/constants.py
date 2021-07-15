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


# define the constants for markers
data = create_constants(
    "data",
    Url="url",
)


# define the constants for environment variables
environment = create_constants(
    "environment", Github_Access_Token="GITHUB_ACCESS_TOKEN", Timezone="LOCAL_TIMEZONE"
)


# define the files constants
files = create_constants(
    "files",
    Env=".env",
)


# define the constants for environment variables
filesystem = create_constants(
    "filesystem",
    All="All",
    Commits="Commits",
    Counts="Counts",
    Csv_Extension=".csv",
    Dash="-",
    Slash="/",
    Results="Results",
    Wildcard="*",
    Workflows="Workflows",
    Zip_Extension=".zip",
)


# define the constants for accessing GitHub
github = create_constants(
    "github",
    Actions="actions/runs",
    Api="api.github.com/repos/",
    Https="https://",
    Maximum_Length_All=3,
    Maximum_Length_Record=25,
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
    Empty=b"",
    Indent="  ",
    Newline="\n",
    Nothing="",
    Space=" ",
    Tab="\t",
    Underscore="_",
)


# define the constants for progress bars
progress = create_constants(
    "progress",
    Bullet="•",
    Completed="completed",
    Elapsed="elapsed",
    Percentage_Format="[progress.percentage]{task.percentage:>3.0f}%",
    Remaining="remaining",
    Task_Format="[progress.description]{task.description}",
)


# define the constants for rate limiting
rate = create_constants(
    "rate",
    Core="core",
    Extra_Seconds=2,
    Limit="limit",
    Used="used",
    Remaining="remaining",
    Reset="reset",
    Resources="resources",
    Rate_Limit_Url="https://api.github.com/rate_limit",
    Threshold=10,
)


# define the constants for workflow
workflow = create_constants(
    "workflow",
    Actions_Url="actions_url",
    Conclusion="conclusion",
    Created_At="created_at",
    Event="event",
    Head_Commit="head_commit",
    Head_Sha="head_sha",
    Jobs_Url="jobs_url",
    Id="id",
    Name="name",
    Organization="organization",
    Repo="repo",
    Repo_Url="repo_url",
    Status="status",
    Updated_At="updated_at",
    Workflow_Build_Count="workflow_build_count",
)


# define the constants for workknow
workknow = create_constants(
    "workknow",
    Emoji=":light_bulb:",
    Https="https://",
    Name="WorkKnow",
    Separator="/",
    Tagline="WorkKnow: Know Your GitHub Actions Workflows!",
    Website="https://github.com/AnalyzeActions/WorkKnow",
)
