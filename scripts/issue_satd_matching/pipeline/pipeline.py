import os
import sys
import json
from itertools import product
from SATDHandler import SATD
from SQHandler import SQ
from time import sleep


SATD_FILE_PATH = '../results/airflow_line_numbers.json'
SONARQUBE_FILES_PATH = '../../satd_commit_pipeline/results/'



def loadJSONFromFile(filepath):
  with open(filepath, "r") as file:
    data = json.load(file)
    return data



if __name__ == '__main__':

  satd = SATD(SATD_FILE_PATH)
  sq = SQ(SONARQUBE_FILES_PATH)

  unique_commits = satd.getUniqueCommits()

  # test_file = 'airflow/www/static/js/gantt.js'
  # test_sha = 'a9314dd63bc62d61ab7b625367f02650274ac99f'

  for commit in unique_commits:
    # Fetch files with SATD in current commit
    satd_files = satd.getFilesByCommit(commit)
    for file in satd_files:
      # Fetch the SATD items corresponding to the current commit and file
      satd_items = satd.filterByCommitAndFilename(commit, file)
      # Fetch SonarQube output for current commit and file
      sonarqube_issues = sq.filterByCommitAndFilename(commit, file)

      for comb in product(satd_items, sonarqube_issues):
        # print("\n", comb)
        # sys.stdout.flush()
        # sleep(1)

        # TODO:
        # Comparison:
        #  - Line distance (threshold parameter)
        #  - Textual similarity scores
        # Results:
        #  - Format and store for manual analysis