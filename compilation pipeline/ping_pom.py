import requests
import os

"""
this script takes all repositories stored in ./repositories.csv 
and pings their github page to test whether they have a pom.xml file. 
if they don't, they're not Maven projects. 
"""

with open("./repositories.csv", "r") as data_file:
    data = [entry.strip().split(",") for entry in data_file.readlines()]

with open("./maven_repositories.csv", "w") as output_file:
    for entry in data[1:]:
        url = os.path.join(
            "https://raw.githubusercontent.com/apache/", entry[0], entry[4], "pom.xml")
        print(url)
        r = requests.get(url)

        if r.status_code == 200:
            print(f'repository {entry[0]} is good')
            output_file.write("Maven\n")
        else:
            output_file.write("Not Maven\n")
            print(f'repository {entry[0]} gave error code {r.status_code}')
