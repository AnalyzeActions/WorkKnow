"""Upload results data as a release to a GitHub repository."""

from pathlib import Path

import logging

from github import Github
from github import GithubException

from workknow import constants
from workknow import request


def create_github_release(
    organization: str, repository: str, semver: str, results_dir: Path
) -> None:
    """Create a new release on GitHub of all files in the results directory."""
    logger = logging.getLogger(constants.logging.Rich)
    github_access_token = request.get_github_personal_access_token()
    github = Github(github_access_token)
    github_repository_name = organization + constants.github.Separator + repository
    logger.debug(github_repository_name)
    github_repository = github.get_repo(github_repository_name)
    # access the list of current files in the repository
    all_files = []
    contents = github_repository.get_contents("")
    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir":
            contents.extend(github_repository.get_contents(file_content.path))
        else:
            file = file_content
            all_files.append(
                str(file).replace('ContentFile(path="', "").replace('")', "")
            )
    logger.debug(all_files)
    results_directory_glob = results_dir.glob("**/*")
    results_files = [x for x in results_directory_glob if x.is_file()]
    results_files_contents = {}
    for results_file in results_files:
        logger.debug(results_file)
        try:
            results_file_contents = results_file.read_text()  # type: ignore
        except UnicodeDecodeError:
            results_file_contents = results_file.read_bytes()  # type: ignore
        results_files_contents[str(results_file.name)] = results_file_contents
    logger.debug(results_files)
    results_files_names = [result_file.name for result_file in results_files]
    logger.debug(results_files_names)
    for result_file_name in results_files_names:
        if result_file_name in all_files:
            try:
                contents = github_repository.get_contents(result_file_name)
            except GithubException:
                contents = get_blob_content(github_repository, "master", result_file_name)
            github_repository.update_file(
                result_file_name,
                "Update WorkKnow Data" + semver,
                results_files_contents[result_file_name],
                contents.sha,
                branch="master",
            )
            logger.debug(result_file_name + " UPDATED")
        else:
            github_repository.create_file(
                result_file_name,
                "Add WorkKnow Data" + semver,
                results_files_contents[result_file_name],
            )
            logger.debug(result_file_name + " CREATED")


def get_blob_content(repo, branch, path_name):
    # first get the branch reference
    ref = repo.get_git_ref(f'heads/{branch}')
    # then get the tree
    tree = repo.get_git_tree(ref.object.sha, recursive='/' in path_name).tree
    # look for path in tree
    sha = [x.sha for x in tree if x.path == path_name]
    if not sha:
        # well, not found..
        return None
    # we have sha
    return repo.get_git_blob(sha[0])
