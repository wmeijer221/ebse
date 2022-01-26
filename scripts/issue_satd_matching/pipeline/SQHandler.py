import os
import sys
import json



class SQ:

  def __init__(self, files_path):
    """Constructor, loads the SonarQube output data from all JSON files in the specified directory"""
    self.directory = files_path
    self.data = {}
    self.loadData(files_path)


  def loadData(self, files_path):
    """Function to gather and load SonarQube output data from multiple JSON files (one per commit)"""
    filenames = os.listdir(files_path)

    for file in filenames:
      key = os.path.splitext(file)[0].split('-')[-1]
      filepath = files_path + file
      self.data[key] = self.loadJSONFromFile(filepath)


  def loadJSONFromFile(self, filepath):
    """Helper function to load JSON data from a file"""
    with open(filepath, "r") as file:
      data = json.load(file)

      return data


  def filterByCommitAndFilename(self, commit_sha, filename):
    """Filters SATD items by commit SHA and filename"""
    key = commit_sha[:8]

    if key not in self.data.keys(): 
      return []

    filtered = [item for item in self.data[key]['issues'] if filename in item['component']]

    return filtered
