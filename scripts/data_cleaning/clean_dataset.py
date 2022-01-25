from sqlite3 import Connection


def clean_dataset(con: Connection):
    cur = con.cursor()

    with open("./repositories.txt", "r") as repositories_file:
        data = [entry.strip() for entry in repositories_file.readlines()]

    git_comment_ids_to_remove = []

    for row in cur.execute(
        f"SELECT id from git_comment WHERE repo_id NOT IN {tuple(data)};"
    ):
        git_comment_ids_to_remove.append(row[0])

    cur.execute(
        f"DELETE from git_comment_satd WHERE id IN {tuple(git_comment_ids_to_remove)};"
    )

    cur.execute(f"DELETE from git_comment WHERE repo_id NOT IN {tuple(data)};")
    cur.execute(f"DELETE from git_commit WHERE repo_id NOT IN {tuple(data)};")
    cur.execute(f"DELETE from git_commit_satd WHERE repo_id NOT IN {tuple(data)};")
    cur.execute(f"DELETE from github_issue WHERE repo_id NOT IN {tuple(data)};")
    cur.execute(f"DELETE from github_issue_comment WHERE repo_id NOT IN {tuple(data)};")
    cur.execute(f"DELETE from github_issue_satd WHERE repo_id NOT IN {tuple(data)};")
    cur.execute(f"DELETE from github_jira_link WHERE repo_id NOT IN {tuple(data)};")
    cur.execute(f"DELETE from github_pull WHERE repo_id NOT IN {tuple(data)};")
    cur.execute(f"DELETE from github_pull_comment WHERE repo_id NOT IN {tuple(data)};")
    cur.execute(f"DELETE from github_pull_review WHERE repo_id NOT IN {tuple(data)};")
    cur.execute(f"DELETE from github_pull_satd WHERE repo_id NOT IN {tuple(data)};")

    con.commit()
