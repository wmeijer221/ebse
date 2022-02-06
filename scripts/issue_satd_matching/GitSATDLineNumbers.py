import sys
import os
import requests
import json
import sqlite3



# INSTRUCTIONS: 
# - Set DATASET_PATH below to the path to the apache.db file (in place of [path/to/apache.db])
# - Add your GitHub API token (in place of [your_api_token]) to disable GitHub API's rate limit
# - Set the desired apache GITHUB_REPO name (i.e. [name] from apache/[name])


DATASET_PATH = '../../../data/apache_cleaned.db'
GITHUB_API_HEADERS = {"Authorization": "token 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"}

GITHUB_REPO = 'tvm'

GITHUB_API_URL = 'https://api.github.com/repositories/'



def getRepoIDByRepoName(repo_name):
  url = 'https://api.github.com/repos/apache/'+ repo_name
  r = requests.get(url, headers=GITHUB_API_HEADERS)

  return json.loads(r.text)['id']


def getChangedFilesByCommit(repo_id, commit_id):
  """Returns the changed file information object from a specific git commit using the GitHub API."""
  url = GITHUB_API_URL + str(repo_id) + '/commits/' + commit_id
  r = requests.get(url, headers=GITHUB_API_HEADERS)

  return json.loads(r.text)['files']


def getChangedFileContentsMultiple(files):
  """Returns the raw contents of multiple files using the changed files' information object.
  (currently unused)"""
  raw_urls = [f['raw_url'] for f in files]
  raw_files = [requests.get(url, headers=GITHUB_API_HEADERS).text for url in raw_urls if url != None]

  return raw_files


def getChangedFileContents(file):
  """Returns the raw contents of a single file using the changed file's information object."""
  url = file['raw_url']
  try:
    raw_file = requests.get(url, headers=GITHUB_API_HEADERS).text
    return raw_file
  except Exception as e:
    print("ERROR: Unable to fetch file contents of file:", file['filename'])
    print(e)
    return ''



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
  result = []

  con = sqlite3.connect(DATASET_PATH)
  cur = con.cursor()

  github_repo_id = getRepoIDByRepoName(GITHUB_REPO)
  print("Repo ID:", github_repo_id)
  sys.stdout.flush()

  # Get and print number of SATD items to process
  q = 'SELECT COUNT(a.id) \
    FROM git_comment a \
    JOIN git_comment_satd b ON a.id = b.id \
    WHERE b.label_id != 0 \
    AND a.repo_id = ' + str(github_repo_id) + ';'

  rows = cur.execute(q)
  satd_item_count = rows.fetchone()[0]

  print('\n\n\t\tPROCESSING', satd_item_count, 'SATD ITEMS...\n\n')
  sys.stdout.flush()


  # Query that collects the git comment SATD items that are to be processed from the dataset
  q = 'SELECT repo_id, sha, comment, b.id, c.label, c.short_label \
    FROM git_comment a \
    JOIN git_comment_satd b ON a.id = b.id \
    JOIN satd_label c ON b.label_id = c.id \
    WHERE b.label_id != 0 \
    AND a.repo_id = ' + str(github_repo_id) + ';'

  rows = cur.execute(q)


  idx = 1
  for row in rows:
    found = False # Flag to indicate if the comment text was found in any of the commit's changed files
    changed_files = getChangedFilesByCommit(row[0], row[1]) # Get list of changed files
    
    # Some printing to show where we're at
    try:
      print("("+str(idx)+"/"+str(satd_item_count)+")", "MATCHES FOR: '", row[2].splitlines()[0][:100], "'")
    except Exception as e:
      print("ERROR")
      print(e)
      print("\n")
      sys.stdout.flush()
      idx += 1
      continue
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
      result.append({'satd_id': row[3], 'satd_repo': row[0], 'satd_sha': row[1],'satd_text': row[2], 'satd_label': row[4],'satd_label_short': row[5], 'file': False, 'lines': False, 'matched_text': None})
      sys.stdout.flush()

    idx += 1

    print("\n")
    sys.stdout.flush()


  print("\n\tDUMPING OUTPUT TO FILE...\n")
  sys.stdout.flush()
  # Output result to JSON file for future use
  with open('./results/' + GITHUB_REPO + '_line_numbers.json', 'w') as outfile:
    json.dump(result, outfile)


  print("\n\t\tDONE!\n")
  sys.stdout.flush()