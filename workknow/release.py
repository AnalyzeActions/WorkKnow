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
    repo_url: str, organization: str, repository: str, semver: str, results_dir: Path
) -> None:
    """Create a new release on GitHub of all files in the results directory."""
    # create a logger for the creation of debugging and error logging
    logger = logging.getLogger(constants.logging.Rich)
    # get a console for use in diagnostic display
    console = configure.setup_console()
    # extract the github_access_token for use during upload process
    github_access_token = request.get_github_personal_access_token()
    github = Github(github_access_token)
    # create the name of the GitHub repository name
    github_repository_name = organization + constants.github.Separator + repository
    logger.debug(github_repository_name)
    # create an instance of the Repository type through the use of PyGithub
    github_repository = github.get_repo(github_repository_name)
    # access the list of current files in the repository
    all_files = []
    contents = github_repository.get_contents("")
    # continue while GitHub reports that there are still files or directories available
    while contents:
        # extract the contents of the current file
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
        # create a default value for the last commit's SHA-1 value, which from
        # the perspective of PyGitHub and the GitHub API is returned as a string
        commit_sha = ""
        # iterate through all of the files that need to be uploaded and EITHER
        # --> Add them to the repository for the first time OR
        # --> Update them in the repository if they already exist
        # NOTE: This approach is going to create an "empty commit" with
        # a message but no changed files when the file is "updated" but,
        # in fact, there are no changes to upload to the repository
        # Reference: https://github.com/PyGithub/PyGithub/issues/661
        for result_file_name in results_files_names:
            # if the current result file is already found in the GitHub
            # then it is important to get its contents and update them
            if result_file_name in all_files:
                # try to get the contents of the file, which will work
                # correctly for text-based files but fail for all large
                # BLOB files returned through the API larger than 1 MB
                try:
                    contents = github_repository.get_contents(result_file_name)
                # attempt to read the file contents again since the previous
                # approach did not work correctly and thus it might be a BLOB
                except GithubException:
                    contents = get_blob_content(
                        github_repository, "main", result_file_name
                    )
                # the contents of the file *should* be accessible now in
                # the variable called "contents" and thus it is okay to call update_file
                logger.debug(result_file_name + " ATTEMPT UPDATE")
                update_dict = github_repository.update_file(
                    result_file_name,
                    "Update WorkKnow Data " + semver + " for " + result_file_name,
                    results_files_contents[result_file_name],
                    contents.sha,  # type: ignore
                    branch="main",
                )
                logger.debug(result_file_name + " UPDATED")
                # the returned update_dict contains a "commits" key that maps to a
                # value that has a "sha" attribute; store this attribute in commit_sha
                # because if this the last commit then this function needs the SHA-1
                # hash to created a tagged release with a semver in the data repository
                commit_sha = update_dict["commit"].sha
            else:
                # create the file since it is not currently inside the GitHub repository
                logger.debug(result_file_name + " ATTEMPT CREATE")
                create_dict = github_repository.create_file(
                    result_file_name,
                    "Add WorkKnow Data " + semver + " for " + result_file_name,
                    results_files_contents[result_file_name],
                )
                # the returned update_dict contains a "commits" key that maps to a
                # value that has a "sha" attribute; store this attribute in commit_sha
                # because if this the last commit then this function needs the SHA-1
                # hash to created a tagged release with a semver in the data repository
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
    console.print()
    console.print(
        f":runner: Creating a tagged release of the data in the repository at: {repo_url}"
    )
    try:
        # create a tag in the GitHub repository and the release all of the files inside
        # of the repository to a release with the designed semver; note that GitHub will
        # automatically create both a .zip and a .tar.gz archive for this release
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
        # accessing the GitHub repository can fail for a wide variety of reasons when
        # creating either a tag or the release. One of the main problems observed so
        # far is that the person using WorkKnow does not correctly specify a unique
        # semver for the release, which will cause the program to crash and enter a
        # state from which it is not possible to recover
        console.print()
        console.print(
            ":grimacing_face: Unable to create a tagged release through the GitHub API"
        )
        console.print(
            constants.markers.Space
            + constants.markers.Space
            + constants.markers.Space
            + "Did you use a unique semantic version number (i.e., semver) for the release?"
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
    # look for the path in the tree
    sha = [x.sha for x in tree if x.path == path_name]
    if not sha:
        # the SHA hash was not found, so return None
        return None
    # return the contents of the BLOB based on the hash value
    return repo.get_git_blob(sha[0])
