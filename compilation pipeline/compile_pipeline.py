from multiprocessing import Array
import os
from git.exc import GitCommandError
from joblib import Parallel, delayed
from git import Repo, GitCommandError
import subprocess
import shutil

"""
Pulls repositories and compiles them using Maven. 
Removes all repositories that could not be compiled, 
resulting in a list of easy-to-compile Maven projects. 
"""


def main():
    """Loads repository data and starts parallelized repo analysis"""

    with open("./repositories.csv", 'r') as data_file:
        data_complete = [entry.split(",") for entry in data_file.readlines()]

    easy_compile = [""] * len(data_complete)

    easy_compile = zip(Parallel(n_jobs=8)(delayed(analysis_lifecycle)
                                          (i, data_complete[i]) for i in range(1, len(data_complete))))

    with open("./easy_repositories.csv", "w") as output_file:
        for result in easy_compile:
            output_file.write(f'{result}\n')


def analysis_lifecycle(index: int, entry: Array):
    """Implements analysis lifecycle for one repository"""

    # generates some params
    name = entry[0]
    url = entry[1]
    dir = os.path.join("./repos/", name)

    print(f'started with repository {name}')

    # perform lifecycle
    clone_repository(url, dir)
    status = build_repository(dir)

    if status != 0:
        print(f'Maven compilation failed for {name}.')
        shutil.rmtree(dir)
        return "No"

    print(f'successfully completed repository {name}')

    return "Yes"


def clone_repository(url: str, dir: str):
    """Clones repository if not yet present"""

    try:
        Repo.clone_from(url, dir)

    except GitCommandError as e:
        if e.status != 128:
            raise e

        print(f'skipped cloning repo for {url} as it is already cloned')


def build_repository(dir: str) -> int:
    """Compiles maven project without running tests"""

    os.chdir(dir)

    args = ['mvn', '-Dmaven.test.skip=true', '-e', 'clean', 'install']
    status = subprocess.call(args=args)

    os.chdir("../..")

    return status


if __name__ == "__main__":
    main()
