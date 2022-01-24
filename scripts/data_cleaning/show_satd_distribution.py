from sqlite3 import Connection
import matplotlib.pyplot as plt


def show_satd_distribution(con: Connection):
    cur = con.cursor()

    table_names = [
        "git_comment_satd",
        "git_commit_satd",
        "github_issue_satd",
        "github_pull_satd",
        "jira_issue_satd",
    ]

    for table_name in table_names:
        occurences = []

        for row in cur.execute(
            f"SELECT label_id, count(label_id) from {table_name} gcs GROUP BY label_id;"
        ):
            occurences.append(row[1])

        total_number_of_items = sum(occurences)
        non_satd = occurences[0]
        yes_satd = total_number_of_items - non_satd
        code_design_satd = occurences[1]
        documentation_satd = occurences[2]
        test_satd = occurences[3]
        requirement_satd = occurences[4]

        print(f"Total satd items: {total_number_of_items}")
        print(f"Non-SATD items: {non_satd}")
        print(f"Code/Design-SATD items: {code_design_satd}")
        print(f"Documentation-SATD items: {documentation_satd}")
        print(f"Test-SATD items: {test_satd}")
        print(f"Requirement-SATD items: {requirement_satd}")

        satd_of_total_percentage = round(100 / total_number_of_items * yes_satd, 2)

        print(f"SATD%: {satd_of_total_percentage}")

        fig1, ax1 = plt.subplots()

        ax1.pie(
            [code_design_satd, documentation_satd, test_satd, requirement_satd],
            labels=[
                "Code/Design-SATD",
                "Documentation-SATD",
                "Test-SATD",
                "Requirement-SATD",
            ],
            autopct="%1.1f%%",
            startangle=90,
        )
        ax1.axis("equal")

        plt.title(table_name)

        plt.savefig(f"{table_name}.png")
