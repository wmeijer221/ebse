import sys
import os
import requests
import json
import sqlite3
from collections import Counter
# from sklearn.feature_extraction.text import CountVectorizer
# from sklearn.metrics.pairwise import cosine_similarity


# INSTRUCTIONS: 
# - Set DATASET_PATH below to the path to the apache.db file (in place of [path/to/apache.db])
# - Add your GitHub API token (in place of [your_api_token]) to disable GitHub API's rate limit

DATASET_PATH = '../../../data/apache.db'
SONARQUBE_RESULTS_PATH = '../compilation pipeline/results/'
SONARQUBE_RESULTS_FILE = 'issues-trafficserver.json'

GITHUB_API_HEADERS = {"Authorization": "token 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"}

GITHUB_API_URL = 'https://api.github.com/repositories/'



def jaccard(str1, str2): 
    a = set(str1.split()) 
    b = set(str2.split())
    c = a.intersection(b)

    return float(len(c)) / (len(a) + len(b) - len(c))


def cosine(*strs): 
    vectors = [t for t in vectorizeStrings(*strs)]

    return cosine_similarity(vectors)

def vectorizeStrings(*strs):
    text = [t for t in strs]
    vectorizer = CountVectorizer(text)
    vectorizer.fit(text)

    return vectorizer.transform(text).toarray()



# def getChangedFilesByCommit(repo_id, commit_id):
  # """Returns the changed file information object from a specific git commit using the GitHub API."""
  


def getChangedFileContentsByCommit(repo_id, commit_id):
  """Returns the raw contents of multiple files using the """
  url = GITHUB_API_URL + str(repo_id) + '/commits/' + commit_id
  r = requests.get(url, headers=GITHUB_API_HEADERS)
  files = json.loads(r.text)['files']
  # raw_urls = [f['raw_url'] for f in files]
  raw_files = {}
  for f in files:
    raw_files[f['filename']] = requests.get(f['raw_url'], headers=GITHUB_API_HEADERS).text
  # raw_files
  # raw_files = [requests.get(url, headers=GITHUB_API_HEADERS).text for url in raw_urls]

  return raw_files


def findStringInFiles(target, files):
  matches = []
  target_split = target.splitlines()

  for filename, content in files.items():
    file_split = content.splitlines()

    for f_line_number, f_line in enumerate(file_split): # Process each line of the input file
      if target_split[0] in f_line: # First line of target matched in the file line -> potential match
        matched_lines = []
        for t_line_number, t_line in enumerate(target_split): # Check subsequent lines against the target string
          offset_line_number = f_line_number + t_line_number # File line number offset with the current line number of the checked potential match
          if offset_line_number < len(file_split) and t_line in file_split[offset_line_number]: # Target line matched in file line
            matched_lines.append(offset_line_number + 1) # + 1 for 1-indexed absolute line numbers
          else:
            break
        if(len(matched_lines) == len(target_split)): # Full-length match found
          # match = (matched_lines, f_line)
          matches.append(filename)

  return matches



if __name__ == '__main__':

  con = sqlite3.connect(DATASET_PATH)
  cur = con.cursor()

  # Query that collects the git comment SATD items that are to be processed from the dataset (LIMIT for development)
  q = 'SELECT repo_id, sha, comment \
    FROM git_comment a \
    JOIN git_comment_satd b ON a.id = b.id \
    WHERE b.label_id != 0 \
    LIMIT 25'

  rows = cur.execute(q)

  for row in rows:
    print(row)
    changed_files = getChangedFileContentsByCommit(row[0], row[1])
    matched_files = findStringInFiles(row[2], changed_files)
    print(matched_files)
    print("\n")
    # print(changed_files.keys())


  sq_output = json.load(open(SONARQUBE_RESULTS_PATH + SONARQUBE_RESULTS_FILE))
  print(sq_output)