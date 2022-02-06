import sys
import os
import requests
import json
import sqlite3
import csv



DATASET_PATH = '../../../data/apache.db'
GITHUB_API_HEADERS = {"Authorization": "token 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"}

GITHUB_API_URL = 'https://api.github.com/repositories/'

CSV_FILE_PATH = './results/satd-count-per-repo.csv'



def getRepoByID(repo_id):
  url = GITHUB_API_URL + str(repo_id)
  r = requests.get(url, headers=GITHUB_API_HEADERS)

  return json.loads(r.text)


if __name__ == '__main__':
  con = sqlite3.connect(DATASET_PATH)
  cur = con.cursor()

  q = 'SELECT a.repo_id, COUNT(a.id) \
    FROM git_comment a \
    JOIN git_comment_satd b ON a.id = b.id \
    WHERE b.label_id != 0 \
    GROUP BY a.repo_id;'

  rows = cur.execute(q)

  csv_rows = []

  for row in rows:
    repo_data = getRepoByID(row[0])
    repo_name = repo_data['name']
    repo_lang = repo_data['language']

    if repo_lang != 'Java':
      csv_rows.append({ \
        'id': row[0], \
        'name': repo_name, \
        '#SATD': row[1], \
        'language': repo_lang, \
        'size': repo_data['size'], \
      })
      print(repo_name, row[0], row[1], repo_lang, repo_data['size'])



  csv_keys = csv_rows[0].keys()

  with open(CSV_FILE_PATH, 'w', newline='') as output_file:
      dict_writer = csv.DictWriter(output_file, csv_keys, delimiter=",")
      dict_writer.writeheader()
      dict_writer.writerows(csv_rows)