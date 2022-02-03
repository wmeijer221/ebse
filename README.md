# Evidence-Based Software Engineering

This project contains code and data related to assignment 2 of the Evidence-Based Software Engineering course. 
It contains a number of small pipeline tools used for data extraction and analysis, all of which is contained in the ``scripts`` folder.

## Contents 
- *Data Cleaning -* 
Used for sampling the original data set (makes it easier to deal with the dataset), and extracting some basic descriptive statistics (SATD type distribution) of it.

- *Extract SATD Commits -* 
Extracts git commit data using the Github API.
Only considers commits for which there is a corresponding SATD item in the data set.

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

The scripts are all used in the above stationed order (excluding the *Compilation Pipeline*, as it's obsolete).
To analyze a single new project, steps 2, 3, 4, and 5 should be repeated.
Currently, there are some manual steps involved in this, however, there's no reason this coulnd't be automated in the future.

Take note that none of these steps are fast. 
Executing the entire pipeline can take several hours. 
The scripts have very poor error handling, meaning that if something goes wrong a step might have to be completely repeated.
A stable internet connection is strongly recommended.

When running the scripts for the first time, you might have to run ``pip install`` to install the necessary packages, or install them manually.
TODO: this could probably be made a little friendlier. 

### Step 1) Filtering data
- copy the data set into ``data_cleaning``, and name it ``apache.db``. 
- navigate to ``data_cleaning``.
- run ``python3 main.py`` in the command line. 

### Step 2) SATD Commit Extracting
- navigate to ``extract_satd_commits``.
- open ``extract_commit_hashes.py`` in an IDE or text editor.
- change ``db_path`` variable to where your data set is stored.
- change ``project_id`` to the desired project; this value corresponds with the github id.
- TODO: where does one get this number from? Elaborate on this, or change the input of the script.
- run ``python3 extract_satd_commits.py`` in the command line and wait.
- a new ``.json`` file will have generated, containing your data in format.

### Step 3) SATD file and line tracing
TODO: This is not the matching step, GitSATDLineNumbers.py script is ran in advance of sonarqube analysis to determine which files need to be analysed for each commit. This needs to be cleaned in the repo.
- navigate to the ``isue_satd_matching`` folder. 
- open ``GitSATDLineNumbers.py``
- change ``DATASET_PATH`` to the path of the data set. 
- change the ``token`` field inside ``GITHUB_API_HEADERS`` to your Github API token
- change the ``repo_id`` inside the ``SQL`` query to the desired repo id; same as in steps 2 and 3.
- run ``python3 GitSATDLineNumbers.py`` in the command line and wait.
- the results will be generated in the ``results`` folder. 

### Step 4) SonarQube Issue Generation per Commit
- launch a SonarQube server (using the Docker image is the easiest) with port 9000 opened.
- navigate to ``satd_commit_pipeline`` folder.
- copy the results from step 2 into the ``input`` folder.
- make sure the ``results`` folder has no files (not necessary, but it makes your life a lot easier).
- open ``pipeline.py``. 
- change the ``git_id`` to the desired project; the same as in step 2
- change the ``proj_uri`` variable to the desired repository uri
- change the ``sq_server`` to the right server uri
- change the ``sq_auth`` to the credentials used in the SonarQube server (default is admin, admin)
- run ``python3 pipeline.py`` in the command line and wait. 
- the results will be generated in multiple ``.json`` files the ``results`` folder.
- you can stop the SonarQube server at this point.


### Step 5) Matching SATDs with SonarQube Issues
TODO: This script was temporary and will be removed. Instead, the matching is done using the pipeline in the ``scripts/issue_satd_matching/pipeline/`` folder. Instructions need to be added once codebase is polished.
~~- navigate to the ``issue_satd_matching`` folder.~~
~~- open ``TextualSimilarity.py``~~
~~- change ``DATASET_PATH`` to the path of the data set.~~ 
~~- change ``SONARQUBE_RESULTS_FILE`` to the correct file.~~ 
~~- change the ``token`` field inside ``GITHUB_API_HEADERS`` to your Github API token. ~~
~~- change or remove the ``LIMIT``clause in the ``SQL`` query at the bottom. ~~
~~- run ``python3 TextualSimilarity.py`` in the command line and wait. ~~
~~- the results will be generated in the ``results`` folder.~~
