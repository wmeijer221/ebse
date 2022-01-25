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
        if offset_line_number < len(file_split) and t_line in file_split[offset_line_number]: # Target line matched in file line
          matched_lines.append(offset_line_number + 1) # + 1 for 1-indexed absolute line numbers
        else:
          break
      if(len(matched_lines) == len(target_split)): # Full-length match found
        match = (matched_lines, f_line)
        matches.append(match)

  return matches



if __name__ == '__main__':
  # print(requests.get('http://api.github.com/rate_limit' , GITHUB_API_HEADERS).text)

  result = []

  con = sqlite3.connect(DATASET_PATH)
  cur = con.cursor()

  # Query that collects the git comment SATD items that are to be processed from the dataset (LIMIT for development)
  q = 'SELECT repo_id, sha, comment, b.id, c.label, c.short_label \
    FROM git_comment a \
    JOIN git_comment_satd b ON a.id = b.id \
    JOIN satd_label c ON b.label_id = c.id \
    WHERE b.label_id != 0 \
    AND a.repo_id = 33884891'
    # LIMIT 10'

  rows = cur.execute(q)

  # print('\n\tPROCESSING', rows.rowcount, 'SATD ITEMS...')

  for row in rows:
    # print(row)
    # result_row = {'satd_id': row[3], 'satd_text': row[2], 'file': None, 'lines': None}
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
        for m in match: 
          print("\t\t\t", m)
          result.append({'satd_id': row[3], 'satd_repo': row[0], 'satd_sha': row[1], 'satd_text': row[2], 'satd_label': row[4],'satd_label_short': row[5], 'file': file['filename'], 'lines': m[0], 'matched_text': m[1]})
        sys.stdout.flush()
    if not found:
      print("\t!!! NO MATCHES FOUND FOR '", row[2].splitlines()[0][:100], "' !!!")
      result.append({'satd_id': row[3], 'satd_text': row[2], 'satd_label': row[4],'satd_label_short': row[5], 'file': False, 'lines': False, 'matched_text': None})
      sys.stdout.flush()

    print("\n")

    sys.stdout.flush()


  print("\n\tDUMPING OUTPUT TO FILE...\n")
  sys.stdout.flush()
  # Output result to JSON file for future use
  with open("./results/airflow_line_numbers.json", "w") as outfile:
    json.dump(result, outfile)


  print("\n\t\tDONE!\n")
  sys.stdout.flush()
  # for r in result:
  #   print(result)
  #   sys.stdout.flush()
