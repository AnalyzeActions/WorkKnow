"""Plugin: Study the correlation between the project's criticality and its build conclusion."""

import pandas

from workknow import configure


def analyze(
    all_counts_df: pandas.DataFrame,
    all_commits_df: pandas.DataFrame,
    all_workflows_df: pandas.DataFrame,
):
    """Plugin: Study the correlation between the project's criticality and its build conclusion."""
    console = configure.setup_console()
    console.print("Running analysis")
