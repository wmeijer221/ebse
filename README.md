# Evidence-Based Software Engineering

This project contains code and data related to assignment 2 of the Evidence-Based Software Engineering course. 
It contains a number of small pipeline tools used for data extraction and analysis, all of which is contained in the ``scripts`` folder.


## Contents 
- *Extract SATD Commits -* 
Extracts git commit data using the Github API.
Only considers commits for which there is a corresponding SATD item in the data set.

- *SATD Tracing -* 
Traces the SATD code comments from the data set to corresponding changed files of the respective commit.

- *SATD Commit Pipeline -* 
Performs SonarQube analysis on specific git commits and specific files within that commit and extracts SonarQube quality issues.
A number of projects are filtered out as they are not considered in this research.

- *Issue SATD Matching -* 
Matches SATD items with SonarQube quality issues, filtering them by line distance, and calculates their Jaccard and Cosine similarity. 

- *Compilation Pipeline -* 
Performs automated SonarQube analysis on a number of git repositories. 
This is no longer used and is replaced by *SATD Commit Pipeline*.


## How to use
For any of this to work, you need the original data set, which can be acquired from Yikun Li at the University of Groningen.
This work used an early version of the data set, for which there's a solid chance the dataset will have changed by the time someone uses this code, so it might no longer be compatible.

Also, in order to run the included SonarQube server, [Docker](https://www.docker.com/get-started) needs to be installed.

The scripts are all used in the above stated order (excluding the *Compilation Pipeline*, as it's obsolete).
To analyze a single new project, steps 2, 3, 4, and 5 should be repeated.
Currently, there are some manual steps involved in this, however, there's no reason this coulnd't be automated in the future.

Take note that none of these steps are fast. 
Executing the entire pipeline can take several hours. 
The scripts have very poor error handling, meaning that if something goes wrong a step might have to be completely repeated.
A stable internet connection is strongly recommended.

When running the scripts for the first time, you might have to run ``pip install`` to install the necessary packages, or install them manually.


### Step 1) SATD Commit Extracting
- navigate to ``extract_satd_commits``.
- open ``extract_commit_hashes.py`` in an IDE or text editor.
- change ``db_path`` variable to where your data set is stored.
- change ``project_id`` to the desired project; this value corresponds with the github id.
- TODO: where does one get this number from? Elaborate on this, or change the input of the script.
- run ``python3 extract_satd_commits.py`` in the command line and wait.
- a new ``.json`` file will have generated, containing your data in format.

### Step 2) SATD file and line tracing
- navigate to the ``satd_tracing`` folder. 
- open ``GitSATDLineNumbers.py`` in an IDE or text editor.
- change ``DATASET_PATH`` to the path of the data set.
- replace ``GITHUB_API_TOKEN`` inside ``GITHUB_API_HEADERS`` to your Github API token.
- change ``GITHUB_REPO`` to the desired GitHub Apache repository name (repo from ``Apache/repo``).
- run ``python3 GitSATDLineNumbers.py`` in the command line and wait.
- the results will be generated in the ``satd_tracing/results`` folder (with a corresponding log in ``/log``). 

### Step 3) SonarQube Issue Generation per Commit
- navigate to the repository's **root** folder. 
- launch a SonarQube server by running ``docker-compose up -d``
- navigate to ``satd_commit_pipeline`` folder.
- copy the results from step 2 into the ``input`` folder.
- make sure the ``results`` folder has no files (not necessary, but it makes your life a lot easier).
- open ``pipeline.py`` in an IDE or text editor. 
- change the ``git_id`` to the desired project; the same as in step 2
- change the ``proj_uri`` variable to the desired repository uri
- change the ``sq_server`` to the right server uri
- change the ``sq_auth`` to the credentials used in the SonarQube server (default is admin, admin)
- run ``python3 pipeline.py`` in the command line and wait. 
- the results will be generated in multiple ``.json`` files the ``results`` folder.
- you can stop the SonarQube server at this point.


### Step 4) Matching SATDs with SonarQube Issues
TODO: This script was temporary and will be removed. Instead, the matching is done using the pipeline in the ``scripts/issue_satd_matching/pipeline/`` folder. Instructions need to be added once codebase is polished.
- navigate to the ``issue_satd_matching/pipeline`` folder.
- open ``pipeline.py`` in an IDE or text editor.
- change ``REPO_NAME`` to the desired GitHub Apache repository name (repo from ``Apache/repo``).
- change ``SATD_FILE_PATH`` to the correct JSON **file** containing the output from step 2 (if it is different from the default location).
- change ``SONARQUBE_FILES_PATH`` to the correct **directory** containing the output from step 3 (if it is different from the default location).
- run ``python3 pipeline.py`` in the command line and wait.
- the results will be generated in the ``issue_satd_matching/results`` folder.
