import sqlite3


def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}


def get_connection():
    con = sqlite3.connect("../commeunpoissondansleau.db")
    con.row_factory = dict_factory
    return con
