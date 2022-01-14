import sys
import os
import requests
import json
import sqlite3


# INSTRUCTIONS: 
# - Set DATASET_PATH below to the path to the apache.db file (in place of [path/to/apache.db])
# - Add your GitHub API token (in place of [your_api_token]) to disable GitHub API's rate limit


DATASET_PATH = '[path/to/apache.db]'
GITHUB_API_HEADERS = {"Authorization": "token [your_api_token]"}

GITHUB_API_URL = 'https://api.github.com/repositories/'



def getChangedFilesByCommit(repo_id, commit_id):
  """Returns the changed file information object from a specific git commit using the GitHub API."""
  url = GITHUB_API_URL + str(repo_id) + '/commits/' + commit_id
  r = requests.get(url, headers=GITHUB_API_HEADERS)

  return json.loads(r.text)['files']


def getChangedFileContentsMultiple(files):
  """Returns the raw contents of multiple files using the changed files' information object.
  (currently unused)"""
  raw_urls = [f['raw_url'] for f in files]
  raw_files = [requests.get(url, headers=GITHUB_API_HEADERS).text for url in raw_urls]

  return raw_files


def getChangedFileContents(file):
  """Returns the raw contents of a single file using the changed file's information object."""
  url = file['raw_url']
  raw_file = requests.get(url, headers=GITHUB_API_HEADERS).text

  return raw_file


def getLineNumberOfStringInFile(target, file):
  """Searches raw file content (string) by line for the occurrence of a target SATD comment's text.
  Returns the line numbers of the lines for full-length target matches."""
  matches = []

  file_split = file.splitlines()
  target_split = target.splitlines()

  for f_line_number, f_line in enumerate(file_split): # Process each line of the input file
    if target_split[0] in f_line: # First line of target matched in the file line -> potential match
      matched_lines = []
      for t_line_number, t_line in enumerate(target_split): # Check subsequent lines against the target string
        offset_line_number = f_line_number + t_line_number # File line number offset with the current line number of the checked potential match
        if t_line in file_split[offset_line_number]: # Target line matched in file line
          matched_lines.append(offset_line_number + 1) # + 1 for 1-indexed absolute line numbers
        else:
          break
      if(len(matched_lines) == len(target_split)): # Full-length match found
        match = (matched_lines, f_line)
        matches.append(match)

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
    found = False # Flag to indicate if the comment text was found in any of the commit's changed files
    changed_files = getChangedFilesByCommit(row[0], row[1]) # Get list of changed files
    
    # Some printing to show where we're at
    print("MATCHES FOR: '", row[2].splitlines()[0][:100], "'")
    url = GITHUB_API_URL + str(row[0]) + '/commits/' + row[1]
    print("\tREFERENCE URL:\t" + url)
    sys.stdout.flush()

    # Process changed files of the SATD comment's commit
    for file in changed_files:
      raw_content = getChangedFileContents(file) # Get raw file content
      match = getLineNumberOfStringInFile(row[2], raw_content) # Find target comment text in file
      if match != []:
        print("\n\t\tIN FILE: '", file['filename'], "'")
        found = True
        for m in match: print("\t\t\t", m)
        sys.stdout.flush()
    if not found:
      print("\t!! NO MATCHES FOUND FOR '", row[2].splitlines()[0][:100], "'")
      sys.stdout.flush()

    print("\n")
    sys.stdout.flush()
