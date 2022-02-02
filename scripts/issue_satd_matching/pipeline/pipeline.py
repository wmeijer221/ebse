import os
import sys
import json
import csv
import warnings
import pandas as pd
from time import sleep
from itertools import product
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from gensim.parsing.preprocessing import remove_stopwords
from SATDHandler import SATD
from SQHandler import SQ



SATD_FILE_PATH = '../results/airflow_line_numbers.json'
SONARQUBE_FILES_PATH = '../../satd_commit_pipeline/results/'

LINEDISTANCE_THRESHOLD = 50

# JACCARD_SIM_THRESHOLD = 0.1
# COSINE_SIM_THRESHOLD = 0.1

WRITE_TO_CSV = True

USE_CSV_REFERENCE = True
REFERENCE_CSV_PATH = '../results/satd-sq-combinations-filtered.csv'
CSV_FILE_PATH = '../results/satd-sq-combinations-filtered-scores.csv'



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
    dist = computeDistance(satd['lines'][0], sq['line'])
    return (dist, dist <= LINEDISTANCE_THRESHOLD)

  elif(len(satd['lines']) > 1):
    start = min(satd['lines'])
    end = max(satd['lines'])

    d_start = computeDistance(start, sq['line'])
    d_end = computeDistance(end, sq['line'])

    dist = min(d_start, d_end)

    return (dist, dist <= LINEDISTANCE_THRESHOLD)


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
  satd_text = remove_stopwords(satd['satd_text'])
  sq_text = remove_stopwords(sq['message'])

  jaccard = computeJaccardSim(satd_text, sq_text)
  cosine = computeCosineSim(satd_text, sq_text)

  return (jaccard, cosine)



if __name__ == '__main__':
  satd = SATD(SATD_FILE_PATH)
  sq = SQ(SONARQUBE_FILES_PATH)

  if USE_CSV_REFERENCE:
    df = pd.read_csv(REFERENCE_CSV_PATH)
    unique_commits = df['commit'].unique()
    print(unique_commits)
  else:
    unique_commits = satd.getUniqueCommits()

  if(WRITE_TO_CSV):
    combs_csv = []

  count = 0

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

        if comb_sq['message'] == 'Complete the task associated to this \"TODO\" comment.':
          continue

        line_distance_match = compareLineDistance(comb_satd, comb_sq)

        if line_distance_match[1]:
          count += 1
          textual_sim = computeTextualSimilarity(comb_satd, comb_sq)
          jaccard_score = textual_sim[0]
          cosine_score = textual_sim[1][0][1]
          print("\n")
          print(comb_satd['satd_text'])
          print(comb_sq['message'])
          print("Jaccard: \n", jaccard_score)
          print("Cosine: \n", cosine_score)
          sys.stdout.flush()


        if(WRITE_TO_CSV and line_distance_match[1]):
          url = 'https://www.github.com/apache/airflow/commit/' + comb_satd['satd_sha']
          csv_line = { \
            'satd_id': comb_satd['satd_id'], \
            'commit': commit, \
            'file': file, \
            'URL': url,\
            'distance': line_distance_match[0], \
            '________': '________', \
            'satd_lines': comb_satd['lines'], \
            'satd_label': comb_satd['satd_label'], \
            'satd_text': comb_satd['satd_text'].replace('\n', '\\n'), \
            '_________': '_________', \
            'sq_line': comb_sq['line'], \
            'sq_issue': comb_sq['message'], \
            '__________': '__________', \
            'jaccard': jaccard_score, \
            'cosine': cosine_score, \
            }
          combs_csv.append(csv_line)

          # sleep(1)


  print(count)

  if(WRITE_TO_CSV):
    csv_keys = combs_csv[0].keys()

    with open(CSV_FILE_PATH, 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, csv_keys, delimiter=",")
        dict_writer.writeheader()
        dict_writer.writerows(combs_csv)