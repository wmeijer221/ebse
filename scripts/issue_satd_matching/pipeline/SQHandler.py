import os
import sys
import json



class SQ:

  def __init__(self, files_path):
    self.directory = files_path
    self.data = {}
    self.loadData(files_path)


  def loadData(self, files_path):
    filenames = os.listdir(files_path)

    for file in filenames:
      key = os.path.splitext(file)[0].split('-')[-1]
      filepath = files_path + file
      self.data[key] = self.loadJSONFromFile(filepath)


  def loadJSONFromFile(self, filepath):
    with open(filepath, "r") as file:
      data = json.load(file)
      return data


  def filterByCommitAndFilename(self, commit_sha, filename):
    key = commit_sha[:8]
    if key not in self.data.keys(): 
      return []

    filtered = [item for item in self.data[key]['issues'] if filename in item['component']]
    return filtered