from subprocess import Popen
import json
import os
import requests
from typing import Tuple
from git import Repo


def read_input(proj_id: str) -> dict:
    with open(f"./input/commits_{proj_id}.json", "r") as input_file:
        return json.loads(input_file.read())


def clone_repository(url: str, proj_name: str) -> str:
    dir = os.path.join("./repos", proj_name)

    repo = Repo(dir) if os.path.exists(dir) else Repo.clone_from(url, dir)

    return dir, repo


def create_sq_project(sq_server: str, auth: Tuple, proj_id: str):
    url = f"{sq_server}/api/projects/create"
    name = f"project-{proj_id}"
    args = {"name": name, "project": name, "visibility": "public"}

    requests.post(url=url, data=args, auth=auth)

    return name


def move_head(proj_repo: Repo, commit: dict):
    hash = commit["sha"]
    proj_repo.git.checkout(hash)
    # Repo.create_head (path=proj_dir, commit=hash, force=True)


def run_sonarqube(sq_server: str, auth: Tuple, dir: str, proj_id: str):
    args = [
        "sonar-scanner",
        "-Dsonar.sources=.",
        f"-Dsonar.projectKey={proj_id}",
        f"-Dsonar.host.url={sq_server}",
        f"-Dsonar.login={auth[0]}",
        f"-Dsonar.password={auth[1]}",
        "-Dsonar.coverage.exclusions=/**.java",
        "-Dsonar.test.exclusions=/**.java",
        "-Dsonar.exclusions=/**.java",
    ]

    os.chdir(dir)

    with Popen(args) as run_sq_process:
        returncode = run_sq_process.returncode

    os.chdir("../" * (len(dir.split("/")) - 1))

    if returncode != 0:
        raise Exception(f"sq returned {returncode}...")


def export_issues(sq_server: str, auth: Tuple, proj_id: str, commit: dict):
    url = f"{sq_server}/api/issues/search"
    data = {"componentKeys": proj_id}
    res = requests.get(url=url, data=data, auth=auth)
    sha = commit["sha"]

    with open(f"./results/p-{proj_id}_c-{sha}.json", "w") as output_file:
        output_file.write(res.text)


if __name__ == "__main__":
    git_id = "33884891"
    proj_uri = "https://github.com/apache/airflow"

    sq_server = "http://sonarqube:9000"
    sq_auth = ("admin", "password")

    proj_id = create_sq_project(sq_server, sq_auth, git_id)
    proj_dir, proj_repo = clone_repository(proj_uri, git_id)

    commits = read_input(git_id)

    for commit in commits:
        print(f'handling {proj_id=}, {commit["sha"]=}')

        move_head(proj_repo, commit)
        run_sonarqube(sq_server, sq_auth, proj_dir, proj_id)
        export_issues(sq_server, sq_auth, proj_id, commit)
