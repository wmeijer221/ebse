import requests
import json
import pandas as pd

data = pd.DataFrame()


def get_repository_info(cur):
    for row in cur.execute("SELECT DISTINCT repo_id from github_pull gp;"):
        r = requests.get(
            f"https://api.github.com/repositories/{row[0]}",
            headers={"Authorization": "token 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"},
        )
        response_object = json.loads(r.text)

        if "full_name" in response_object.keys():
            new_row = {
                "repo_id": response_object["id"],
                "full_name": response_object["full_name"],
                "git_url": response_object["git_url"],
            }

            data = data.append(response_object, ignore_index=True)

            print(response_object["full_name"])


print(data)
data.to_csv("out.csv", index=False)
