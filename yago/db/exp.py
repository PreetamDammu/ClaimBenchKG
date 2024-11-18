import os
import sqlite3
import argparse

from constants.main import DB_NAME

def create_db(connection):
    cursor = connection.cursor()
    query = 'select sqlite_version();'
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    return result

def main(args):
    connection = sqlite3.connect(args.database)
    res = create_db(connection)
    print(f"SQLite Version: {res}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", default=DB_NAME)
    args = parser.parse_args()

    main(args)