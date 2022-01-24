import json
import sqlite3
from sqlite3 import Connection, Cursor
from typing import Tuple


def connectdb(db_path: str) -> Tuple[Connection, Cursor]:
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    return con, cur


def extract_commits(cur: Cursor, project_id: str) -> Cursor:
    query = f"SELECT * FROM git_comment a \
            JOIN git_comment_satd b ON a.id = b.id \
            WHERE repo_id = {project_id} \
            AND b.label_id != 0;"

    rows = cur.execute(query)

    return rows


def write_to_file(db_results: Cursor, project_id: str) -> None:
    des = db_results.description
    output = []

    rows_processed = 0
    for row in db_results:
        rows_processed += 1

        entry = {}
        for i in range(len(des)):
            cell = str(row[i])
            label = str(des[i][0])
            entry[label] = cell

        output.append(entry)

    with open(f"./commits_{project_id}.json", "w") as output_file:
        output_file.write(json.dumps(output, indent=2))


if __name__ == "__main__":
    db_path = "../../apache.db"
    project_id = "33884891"

    con, cur = connectdb(db_path)
    commits = extract_commits(cur, project_id)
    write_to_file(commits, project_id)
