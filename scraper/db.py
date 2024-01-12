import sqlite3
import os


def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}


def get_connection():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, "../commeunpoissondansleau.db")
    con = sqlite3.connect(db_path)
    con.row_factory = dict_factory
    return con
