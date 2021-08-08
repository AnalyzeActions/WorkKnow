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
    repo_dict_list = []
    if "conclusion" in all_workflows_df:
        dfkeep = all_workflows_df[["organization", "repo", "status", "conclusion"]]
        logger.debug(dfkeep)
        groupby = (
            dfkeep.groupby(["organization", "repo", "conclusion"], as_index=True).agg(
                ["count"]
            )
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
        repositories = groupby["repo"].unique()
        logger.debug(repositories)
        for repository in repositories:
            repo_dict = {}
            repo_group = groupby.loc[lambda df: df["repo"] == repository]
            repo_group_failure = repo_group.loc[repo_group["conclusion"] == "failure"]
            repo_group_failure_count = repo_group_failure["status"].values[0][0]
            logger.debug(repo_group)
            logger.debug(f"repo group failure: {repo_group_failure}")
            logger.debug(f"*** failure count: {repo_group_failure_count}")
            # repo_group_not_failure = repo_group.loc[
            #     repo_group["conclusion"] != "failure"
            # ]
            repo_group_not_failure = repo_group[
                ~repo_group.conclusion.isin(["failure"])
            ]
            if not repo_group_not_failure.empty:
                repo_group_not_failure_count = groupby["status"].sum()
            else:
                repo_group_not_failure_count = 0
            logger.debug(f"repo group not failure: {repo_group_not_failure}")
            logger.debug(f"*** not failure count: {repo_group_not_failure_count}")
            repo_dict["repo"] = repository
            organization_name = repo_group["organization"].unique().tolist()[0]
            logger.debug(f"org value: {organization_name}")
            repo_dict["organization"] = organization_name
            failure_percentage = (repo_group_failure_count) / (
                repo_group_failure_count + repo_group_not_failure_count
            )
            logger.debug("calculated failure percentage: " + str(failure_percentage))
            repo_dict["failure_percentage"] = failure_percentage
            repo_dict_list.append(repo_dict)
            # groupby.loc[(groupby["repo"] == repository), "percent_failure"] = 27
        logger.debug(f"groupby modified = {groupby}")
    return_value_df = pandas.DataFrame(repo_dict_list)
    logger.debug(return_value_df)
    console.print(return_value_df)
    return (return_value_df, "stats", True)
