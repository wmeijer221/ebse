import os
import sys
import json


class SATD:

  def __init__(self, filepath):
    """Constructor, loads the SATD item data from the specified JSON file path"""
    self.data = self.loadJSONFromFile(filepath)


  def loadJSONFromFile(self, filepath):
    """Helper function to load JSON data from a file"""
    with open(filepath, "r") as file:
      data = json.load(file)

      return data


  def filterByCommitAndFilename(self, commit_sha, filename):
    """Filters SATD items by commit SHA and filename"""
    items = [item for item in self.data if 'satd_sha' in item.keys() \
      and item['satd_sha'] == commit_sha \
      and item['file'] == filename]

    return items


  def getUniqueCommits(self):
    """Returns a list of unique commit SHA's in the SATD data"""
    items = list(set([item['satd_sha'] for item in self.data if item['file']]))

    return items


  def getUniqueFiles(self):
    """Returns a list of unique filenames in the SATD data"""
    items = list(set([item['file'] for item in self.data if item['file']]))

    return items


  def getFilesByCommit(self, commit_sha):
    """Returns the files corresponding to the specified commit SHA"""
    items = list(set([item['file'] for item in self.data if item['file'] \
      and 'satd_sha' in item.keys() \
      and item['satd_sha'] == commit_sha]))

    return items
