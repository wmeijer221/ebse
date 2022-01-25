import os
import sys
import json
from SATDHandler import SATD
from SQHandler import SQ


SATD_FILE_PATH = '../results/airflow_line_numbers.json'
SONARQUBE_FILES_PATH = '../../satd_commit_pipeline/results/'



def loadJSONFromFile(filepath):
  with open(filepath, "r") as file:
    data = json.load(file)
    return data



if __name__ == '__main__':

  satd = SATD(SATD_FILE_PATH)
  sq = SQ(SONARQUBE_FILES_PATH)

  test_file = 'airflow/www/static/js/gantt.js'
  test_sha = 'a9314dd63bc62d61ab7b625367f02650274ac99f'

  for x in sq.filterByCommitAndFilename(test_sha, test_file):
    print(x)