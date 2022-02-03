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

The scripts are all used in the above stationed order (excluding the *Compilation Pipeline*, as it's obsolete).
To analyze a single new project, steps 2, 3, and 4 should be repeated.
Currently, there are some manual steps involved in this, however, there's no reason this coulnd't be automated in the future. 

### Step 1) Filtering data
- copy the data set into ``data_cleaning``, and name it ``apache.db``. 
- navigate to ``data_cleaning``.
- run ``python3 main.py`` in the command line. 

### Step 2) SATD Commit Extracting
- navigate to ``extract_satd_commits``.
- open ``extract_commit_hashes.py``.
- change ``db_path`` variable to where your data set is stored.
- change ``project_id`` to the desired project; this value corresponds with the github id.
- TODO: where does one get this number from?

### Step 3) 
