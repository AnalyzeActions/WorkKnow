"""Plugin: Study the correlation between the project's criticality and its build conclusion."""

import logging

import pandas

from typing import Tuple


from workknow import constants


def analyze(
    all_counts_df: pandas.DataFrame,
    all_commits_df: pandas.DataFrame,
    all_workflows_df: pandas.DataFrame,
) -> Tuple[pandas.DataFrame, str, bool]:
    """Plugin: Study the correlation between the project's criticality and its build conclusion."""
    # create a logger and a console for output
    logger = logging.getLogger(constants.logging.Rich)
    logger.debug(all_workflows_df.columns.tolist())
    # create a list of dictionaries that will store data about the repositories
    # and ultimately be converted to a Pandas data frame for function's output
    repo_dict_list = []
    # the data frame of the workflows contains the "conclusion", which is the final
    # status of the build inside of GitHub Actions; this means the tool can extract it
    if "conclusion" in all_workflows_df:
        # extract the attributes about the workflows needed for this analysis, discarding
        # the other attributes that are not needed for the analysis, making output and the
        # statistical analysis easier to conduct and understand
        workflows_keep = all_workflows_df[
            ["organization", "repo", "status", "conclusion"]
        ]
        # using the attributes that were previously chosen as keepers, group the data so
        # that it is possible to see the number of different conclusions for each project;
        # note that it is important to run reset_index so that this makes indexable a data frame
        groupby = (
            workflows_keep.groupby(
                ["organization", "repo", "conclusion"], as_index=True
            ).agg(["count"])
        ).reset_index()
        # get a list of the unique repositories inside of the workflows data set
        repositories = groupby["repo"].unique()
        # iterate through each of the repositories, extracting relevant data and then
        # iteratively creating the data frame that will be return from this plugin
        for repository in repositories:
            # create an empty dictionary for this specific repository that will be
            # populated with (key, value) pairs and then added to the final list of
            # dictionaries that will be converted to the returned data frame
            repo_dict = {}
            # extract the criticality score for this specific repository by looking
            # in the data frame that contains the all counts data
            repo_group_criticality = all_counts_df.loc[
                lambda df: df["name"] == repository
            ]
            # extract the specific criticality score from the extracted data frame
            repo_group_criticality_score = repo_group_criticality["criticality_score"]
            # extract the data that is specifically related to this repository
            repo_group = groupby.loc[lambda df: df["repo"] == repository]
            # count the number of failures associated with builds for this repository
            repo_group_failure = repo_group.loc[repo_group["conclusion"] == "failure"]
            repo_group_failure_count = repo_group_failure["status"].values[0][0]
            # count the number of failures not associated with builds for this repository
            repo_group_not_failure = repo_group[
                ~repo_group.conclusion.isin(["failure"])
            ]
            # if there are some build conclusions not related to failure then extract
            # all of their counts and then sum them to get the non-failure count
            if not repo_group_not_failure.empty:
                repo_group_not_failure_count = groupby["status"].sum()
            # there were no counts that were not related to failures and thus
            # the tool must assume that the number of non-failures in 0
            else:
                repo_group_not_failure_count = 0
            # store the name of the repository in the dictionary
            repo_dict["repo"] = repository
            # store the name of the organization in the dictionary
            organization_name = repo_group["organization"].unique().tolist()[0]
            repo_dict["organization"] = organization_name
            # calculate the failure percentage and store it in the dictionary
            failure_percentage = (repo_group_failure_count) / (
                repo_group_failure_count + repo_group_not_failure_count
            )
            repo_dict["failure_percentage"] = failure_percentage
            repo_dict["criticality_score"] = repo_group_criticality_score
            # add the currently created dictionary to the list of dictionaries
            repo_dict_list.append(repo_dict)
        logger.debug(f"groupby modified = {groupby}")
    # create a pandas DataFrame from the list of dictionaries
    return_value_df = pandas.DataFrame(repo_dict_list)
    return (return_value_df, "stats", True)
