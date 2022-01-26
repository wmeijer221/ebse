import os
import sys
import json
import csv
import warnings
from time import sleep
from itertools import product
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from SATDHandler import SATD
from SQHandler import SQ



SATD_FILE_PATH = '../results/airflow_line_numbers.json'
SONARQUBE_FILES_PATH = '../../satd_commit_pipeline/results/'

LINEDISTANCE_THRESHOLD = 5

JACCARD_SIM_THRESHOLD = 0.15
# COSINE_SIM_THRESHOLD = 

WRITE_TO_CSV = False
CSV_FILE_PATH = '../results/satd-sq-combinations.csv'



def loadJSONFromFile(filepath):
  """Helper function to load JSON data from a file"""
  with open(filepath, "r") as file:
    data = json.load(file)

    return data


def computeDistance(x, y):
  """Computes distance between two (line) numbers"""
  return abs(x - y)


def compareLineDistance(satd, sq):
  """Checks whether the line distance between an SATD comment and SonarQube issue exceeds the threshold or not"""
  if(len(satd['lines']) == 1):
    return computeDistance(satd['lines'][0], sq['line']) <= LINEDISTANCE_THRESHOLD

  elif(len(satd['lines']) > 1):
    start = min(satd['lines'])
    end = max(satd['lines'])

    return ( \
      (computeDistance(start, sq['line']) <= LINEDISTANCE_THRESHOLD) \
      or (computeDistance(end, sq['line']) <= LINEDISTANCE_THRESHOLD))


def computeJaccardSim(str1, str2):
  """Computes the Jaccard textual similarity metric"""
  a = set(str1.split()) 
  b = set(str2.split())
  c = a.intersection(b)

  return float(len(c)) / (len(a) + len(b) - len(c))


def computeCosineSim(*strs):
  """Computes the cosine textual similarity metric"""
  vectors = [t for t in vectorizeStrings(*strs)]

  return cosine_similarity(vectors)


def vectorizeStrings(*strs):
  """Vectorizes strings for the cosine similarity computation"""
  text = [t for t in strs]
  # text = strs
  with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    vectorizer = CountVectorizer(text)
    vectorizer.fit(text)

  return vectorizer.transform(text).toarray()


def computeTextualSimilarity(satd, sq):
  """Computes the textual similarity metrics between an SATD comment and SonarQube issue"""
  satd_text = satd['satd_text']
  sq_text = sq['message']

  jaccard = computeJaccardSim(satd_text, sq_text)
  cosine = computeCosineSim(satd_text, sq_text)

  return (jaccard, cosine)



if __name__ == '__main__':
  satd = SATD(SATD_FILE_PATH)
  sq = SQ(SONARQUBE_FILES_PATH)

  unique_commits = satd.getUniqueCommits()


  # test_file = 'airflow/www/static/js/gantt.js'
  # test_sha = 'a9314dd63bc62d61ab7b625367f02650274ac99f'


  if(WRITE_TO_CSV):
    combs_csv = []


  for commit in unique_commits:
    # Fetch files with SATD in current commit
    satd_files = satd.getFilesByCommit(commit)
    for file in satd_files:
      # Fetch the SATD items corresponding to the current commit and file
      satd_items = satd.filterByCommitAndFilename(commit, file)
      # Fetch SonarQube output for current commit and file
      sonarqube_issues = sq.filterByCommitAndFilename(commit, file)
      # print(sonarqube_issues)
      for comb in product(satd_items, sonarqube_issues):
        comb_satd = comb[0]
        comb_sq = comb[1]


        line_distance_match = compareLineDistance(comb_satd, comb_sq)
        textual_sim = computeTextualSimilarity(comb_satd, comb_sq)

        # if line_distance_match:
        #   print(commit, file, comb_satd['lines'], comb_sq['line'], line_distance_match)
        #   sys.stdout.flush()

        # if textual_sim[0] > 0.15:
        #   print("\n")
        #   print(comb_satd['satd_text'])
        #   print(comb_sq['message'])
        #   print("Jaccard: \n", textual_sim[0])
        #   print("Cosine: \n", textual_sim[1])
        #   sys.stdout.flush()


        if(WRITE_TO_CSV):
          csv_line = { \
            'satd_id': comb_satd['satd_id'], \
            'commit': commit, \
            'file': file, \
            '________': '________', \
            'satd_lines': comb_satd['lines'], \
            'satd_label': comb_satd['satd_label'], \
            'satd_text': comb_satd['satd_text'].replace('\n', '\\n'), \
            '_________': '_________', \
            'sq_line': comb_sq['line'], \
            'sq_issue': comb_sq['message'], \
            }
          combs_csv.append(csv_line)

          sleep(1)


  if(WRITE_TO_CSV):
    csv_keys = combs_csv[0].keys()

    with open(CSV_FILE_PATH, 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, csv_keys, delimiter=";")
        dict_writer.writeheader()
        dict_writer.writerows(combs_csv)