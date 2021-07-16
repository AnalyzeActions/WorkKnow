"""Upload results data as a release to a GitHub repository."""

from pathlib import Path

import logging
import sys

from rich.progress import BarColumn
from rich.progress import Progress
from rich.progress import TimeRemainingColumn
from rich.progress import TimeElapsedColumn

from github import Github
from github import GithubException
from github import InputGitAuthor

from workknow import configure
from workknow import constants
from workknow import request


def perform_github_upload(
    organization: str, repository: str, semver: str, results_dir: Path
) -> None:
    """Create a new release on GitHub of all files in the results directory."""
    # create a logger
    logger = logging.getLogger(constants.logging.Rich)
    # get a console for use in diagnostic display
    console = configure.setup_console()
    # extract the github_access_token for use during upload process
    github_access_token = request.get_github_personal_access_token()
    github = Github(github_access_token)
    github_repository_name = organization + constants.github.Separator + repository
    logger.debug(github_repository_name)
    github_repository = github.get_repo(github_repository_name)
    # access the list of current files in the repository
    all_files = []
    contents = github_repository.get_contents("")
    while contents:
        file_content = contents.pop(0)  # type: ignore
        if file_content.type == "dir":
            contents.extend(github_repository.get_contents(file_content.path))  # type: ignore
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
    with Progress(
        constants.progress.Task_Format,
        BarColumn(),
        constants.progress.Percentage_Format,
        constants.progress.Completed,
        "•",
        TimeElapsedColumn(),
        "elapsed",
        "•",
        TimeRemainingColumn(),
        "remaining",
    ) as progress:
        upload_pages_task = progress.add_task("Upload", total=len(results_files_names))
        commit_sha = 0
        for result_file_name in results_files_names:
            # result_file_name_prefixed = "results/" + result_file_name
            if result_file_name in all_files:
                try:
                    contents = github_repository.get_contents(result_file_name)
                except GithubException:
                    contents = get_blob_content(
                        github_repository, "main", result_file_name
                    )
                update_dict = github_repository.update_file(
                    result_file_name,
                    "Update WorkKnow Data " + semver + " for " + result_file_name,
                    results_files_contents[result_file_name],
                    contents.sha,  # type: ignore
                    branch="main",
                )
                logger.debug(result_file_name + " UPDATED")
                commit_sha = update_dict["commit"].sha
            else:
                create_dict = github_repository.create_file(
                    result_file_name,
                    "Add WorkKnow Data " + semver + " for " + result_file_name,
                    results_files_contents[result_file_name],
                )
                commit_sha = create_dict["commit"].sha
                logger.debug(result_file_name + " CREATED")
            progress.update(upload_pages_task, advance=1)
    # create a GitHub author for use in creating the tagged release of the repository
    # note that the date for the InputGitAuthor was extracted from this web site:
    # https://docs.github.com/en/rest/reference/git#tags
    # since it would ensure that the datetime was in the required format
    input_git_author = InputGitAuthor(
        "Gregory M. Kapfhammer", "gkapfham@allegheny.edu", "2014-11-07T22:01:45Z"
    )
    # create a GitHub release that will produce a .zip and .tar.gz file of all the
    # contents of the repository at the specific tag of the provided semver
    try:
        github_repository.create_git_tag_and_release(
            semver,
            "WorkKnow Default Tag Message",
            "WorkKnow Data Release " + semver,
            "WorkKnow automatically released data at version " + semver,
            str(commit_sha),
            "Type",
            input_git_author,
            False,
            False,
        )
    except GithubException:
        console.print()
        console.print(":grimacing_face: Unable to create a tagged release through the GitHub API")
        console.print(
            "Did you use a unique semantic version number (i.e., semver) for the release?"
            + constants.markers.Newline
            + constants.markers.Newline
            + ":sad_but_relieved_face: Exiting now!"
        )
        console.print()
        sys.exit(1)



def get_blob_content(repo, branch, path_name):
    """Extract the blob content's using an extracted SHA-1 hash."""
    # Reference:
    # https://github.com/PyGithub/PyGithub/issues/661
    # get the branch reference for the Github instance in repo
    ref = repo.get_git_ref(f"heads/{branch}")
    # get the tree of the entire Git repository
    tree = repo.get_git_tree(ref.object.sha, recursive="/" in path_name).tree
    # look for path in tree
    sha = [x.sha for x in tree if x.path == path_name]
    if not sha:
        # the SHA hash was not found, so return None
        return None
    # return the contents of the blob based on the hash value
    return repo.get_git_blob(sha[0])
