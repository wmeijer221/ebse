"""
Performs SonarQube analysis per commit on the files 
that have SATD items linked to it. 
Expects the output generated with ``GitSATDLineNumbers.py``'s 
output as input. 
"""

import shutil
from subprocess import Popen
import json
import os
from time import sleep
import requests
from typing import Tuple
from git import Repo


def read_input(proj_id: str) -> dict:
    """Reads input file as json"""

    path = os.path.abspath(f"./input/commitss_{proj_id}.json")
    with open(path, "r") as input_file:
        return json.loads(input_file.read())


def interpret_data(data: list) -> dict:
    """Transforms json data to be separated per commit."""

    reformat = {}

    for entry in data:
        # Entries that could not be linked to a file
        # are ignored.
        if not entry["file"]:
            continue

        sha = entry["satd_sha"]

        if sha in reformat:
            reformat[sha].append(entry)
        else:
            reformat[sha] = [entry]

    return reformat


def clone_repository(url: str, proj_name: str) -> str:
    """Clones repository"""

    dir = os.path.join("./repos", proj_name)
    dir = os.path.abspath(dir)

    repo = Repo(dir) if os.path.exists(dir) else Repo.clone_from(url, dir)

    return dir, repo


def create_sq_project(sq_server: str, auth: Tuple, proj_id: str) -> str:
    """Creates a SonarQube project for the current project"""

    url = f"{sq_server}/api/projects/create"
    name = f"project-{proj_id}"
    args = {"name": name, "project": name, "visibility": "public"}

    requests.post(url=url, data=args, auth=auth)

    return name


def move_head(proj_repo: Repo, sha: str):
    """Moves Repository head to different commit"""

    proj_repo.git.checkout(sha, force=True)


def copy_changed_files(entries: list, dir: str) -> Tuple[str, int]:
    """Copies relevant files to the analysis folder"""

    targetdir = os.path.abspath("./tmp/analysis-folder")
    if os.path.exists(targetdir):
        shutil.rmtree(targetdir)

    try:
        os.mkdir(targetdir)
    except:
        pass

    moved_files = 0

    for entry in entries:
        file = entry["file"]
        from_path = os.path.join(dir, file)

        # TODO: check for is_deleted field.
        # Files that do not exist are ignored.
        if not os.path.exists(from_path):
            continue

        to_path = os.path.join(targetdir, file)

        os.makedirs(os.path.dirname(to_path), exist_ok=True)
        shutil.copy(from_path, to_path)

        moved_files += 1

    return targetdir, moved_files


def run_sonarqube(sq_server: str, auth: Tuple, dir: str, proj_id: str):
    """Runs SonarQube analysis on the test folder."""

    args = [
        "sonar-scanner",
        "-Dsonar.sources=.",
        f"-Dsonar.projectKey={proj_id}",
        f"-Dsonar.host.url={sq_server}",
        f"-Dsonar.login={auth[0]}",
        f"-Dsonar.password={auth[1]}",
        "-Dsonar.coverage.exclusions=/**.java",
        "-Dsonar.test.exclusions=/**.java",
        "-Dsonar.scm.exclusions.disabled=true",
        "-Dsonar.exclusions=/**.java",
    ]

    old_dir = os.path.abspath(os.curdir)
    os.chdir(dir)
    Popen(args).wait()
    os.chdir(old_dir)


def export_issues(sq_server: str, auth: Tuple, proj_id: str, sha: str):
    """Exports SonarQube issues to a file."""

    measures_url = f"{sq_server}/api/measures/component_tree"
    measures_data = {"component": proj_id, "qualifiers": "FIL", "metricKeys": "ncloc,complexity,violations,duplicated_blocks,code_smells,bugs,vulnerabilities"}

    success = False
    retry_counter = 0

    while not success:
        measures_res = requests.get(url=measures_url, params=measures_data, auth=auth)
        response_object = measures_res.json()

        is_analyses_ready = response_object['paging']['total']

        if is_analyses_ready or retry_counter > 2:
            success = True
        else:
            print("Did not receive components, retrying in 3 seconds...")
            retry_counter += 1
            sleep(3)

    components = response_object["components"]

    issues_url = f"{sq_server}/api/issues/search"
    issues_data = {"componentKeys": proj_id}

    res = requests.get(url=issues_url, data=issues_data, auth=auth)
    response_object = res.json()

    response_object["components"] = components

    path = os.path.abspath(f"./results/{proj_id}_c-{sha[:8]}.json")
    with open(path, "w") as output_file:
        output_file.write(json.dumps(response_object))


def delete_sq_project(proj_name: str, sq_server: str, sq_auth: Tuple):
    """Deletes SonarQube project."""

    url = f"{sq_server}/api/projects/delete"
    data = {"project": proj_name}
    requests.post(url=url, data=data, auth=sq_auth)


def main(git_id: str, proj_uri: str, sq_server: str, sq_auth: Tuple):
    """Performs SonarQube analysis lifecycle."""

    proj_dir, proj_repo = clone_repository(proj_uri, git_id)

    commits = read_input(git_id)
    data = interpret_data(commits)

    delete_sq_project(f"project-{git_id}", sq_server, sq_auth)

    for sha, entries in data.items():
        print(f'\n{"=" * 90}\nHANDLING ({git_id=}, {sha=})\n{"=" * 90}\n')

        proj_id = create_sq_project(sq_server, sq_auth, git_id)

        if len(entries) == 0:
            print("Commit has no valid SATD entries.")
            continue

        move_head(proj_repo, sha)
        targetdir, moved_files = copy_changed_files(entries, proj_dir)

        if moved_files == 0:
            print("Zero files could be moved to analysis directory.")
            continue

        run_sonarqube(sq_server, sq_auth, targetdir, proj_id)
        export_issues(sq_server, sq_auth, proj_id, sha)

        delete_sq_project(proj_id, sq_server, sq_auth)

if __name__ == "__main__":
    # By default, performs SonarQube analysis on
    # Apache Airflow.
    git_id = "33884891"
    proj_uri = "https://github.com/apache/airflow"

    sq_server = "http://sonarqube:9000"
    sq_auth = ("admin", "password")

    main(git_id, proj_uri, sq_server, sq_auth)
