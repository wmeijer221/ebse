import sqlite3

from show_satd_distribution import show_satd_distribution

con = sqlite3.connect("./apache.db")

show_satd_distribution(con)

con.close()
