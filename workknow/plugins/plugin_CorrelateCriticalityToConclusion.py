"""Plugin: Study the correlation between the project's criticality and its build conclusion."""

import pandas

from typing import Tuple

from workknow import configure


def analyze(
    all_counts_df: pandas.DataFrame,
    all_commits_df: pandas.DataFrame,
    all_workflows_df: pandas.DataFrame,
) -> Tuple[pandas.DataFrame, str, bool]:
    """Plugin: Study the correlation between the project's criticality and its build conclusion."""
    console = configure.setup_console()
    console.print("Running analysis")
