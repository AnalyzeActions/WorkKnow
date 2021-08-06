"""Plugin: Study the correlation between the project's criticality and its build conclusion."""

import logging

import pandas

from typing import Tuple


from workknow import constants
from workknow import configure


def analyze(
    all_counts_df: pandas.DataFrame,
    all_commits_df: pandas.DataFrame,
    all_workflows_df: pandas.DataFrame,
) -> Tuple[pandas.DataFrame, str, bool]:
    """Plugin: Study the correlation between the project's criticality and its build conclusion."""
    logger = logging.getLogger(constants.logging.Rich)
    console = configure.setup_console()
    logger.debug(f"All counts {all_counts_df}")
    logger.debug(f"All commits {all_commits_df}")
    logger.debug(f"All workflows {all_workflows_df}")
    logger.debug(all_workflows_df.columns.tolist())
    if "conclusion" in all_workflows_df:
        dfkeep = all_workflows_df[["organization", "repo", "status", "conclusion"]]
        logger.debug(dfkeep)
        groupby = (
            dfkeep
            .groupby(["organization", "repo", "conclusion"], as_index=True)
            .agg(["count"])
        ).reset_index()
        pandas.set_option("display.max_columns", None)
        pandas.set_option("display.max_rows", None)
        logger.debug(all_workflows_df)
        logger.debug(groupby)
        console.print()
        console.print(groupby)
        console.print(type(groupby))
        if "conclusion" in groupby:
            console.print("here")
            console.print(groupby)
            logger.debug(groupby.columns.tolist())
        else:
            console.print("not there")
    return_value_df = pandas.DataFrame()
    return (return_value_df, "stats", True)
