import sqlite3 
from sqlite3 import (Connection, Cursor)
from typing import Tuple

def connectdb(db_path: str) ->Tuple[Connection, Cursor]:
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

def write_to_file(results: Cursor, project_id: str) -> None: 
    with open(f"./output/commits_{project_id}.txt", "w") as output_file: 
        output_file.writelines(results)

if __name__ == "__main__": 
    db_path = "~/Downloads/apache.db"
    project_id = "33884891"

    con, cur = connectdb(db_path)
    commits = extract_commits(cur, project_id)
    write_to_file(commits, project_id)
