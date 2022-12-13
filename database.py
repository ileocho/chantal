
import sqlite3, os
from sqlite3 import Error




def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)

    return conn


conn = create_connection(os.getcwd()+'\\agenda.db')
cursor = conn.cursor()
