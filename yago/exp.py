import os
import sqlite3
import argparse

from db.constants.main import DB_NAME

def create_db(connection):
    cursor = connection.cursor()
    query = 'select sqlite_version();'
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    return result

def query_db(connection, query):
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    return result

def main(args):
    connection = sqlite3.connect(args.database)
    # res = create_db(connection)
    # query = "select count(item_id) from items;"
    # query = "select * from items limit 10;"
    # query = "select * from items order by count desc limit 10;"
    # query = """select type, name, tbl_name, sql
    #     FROM sqlite_master
    #     WHERE type='index'"""
    # query = "alter table properties add column count INTEGER DEFAULT 0;"
    # query = "PRAGMA table_info([properties]);"
    query = "select * from properties"

    res = query_db(connection, query)
    with open("output.txt", "w") as f:
        for r in res:
            f.write(str(r) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", default=DB_NAME)
    args = parser.parse_args()

    main(args)