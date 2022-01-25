import os
import sys
import json


class SATD:

  def __init__(self, filepath):
    self.data = self.loadJSONFromFile(filepath)


  def loadJSONFromFile(self, filepath):
    with open(filepath, "r") as file:
      data = json.load(file)
      return data

  def filterByCommitAndFilename(self, commit_sha, filename):
    items = [item for item in self.data if 'satd_sha' in item.keys() \
      and item['satd_sha'] == commit_sha \
      and item['file'] == filename]
    return items