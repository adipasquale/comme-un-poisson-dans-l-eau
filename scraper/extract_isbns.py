import json
from dotenv import load_dotenv
import sqlite3
import logging
from db import get_connection

load_dotenv()
logging.basicConfig(level=logging.INFO)
con = get_connection()
cur = con.cursor()

try:
    cur.execute("ALTER TABLE ressources ADD COLUMN isbn TEXT")
except sqlite3.OperationalError:
    pass

for ressource in cur.execute("SELECT * FROM ressources WHERE google_books_json IS NOT NULL").fetchall():
    data = json.loads(ressource["google_books_json"])
    isbn = None
    for id in data["volumeInfo"]["industryIdentifiers"]:
        if id["type"] == "ISBN_13":
            isbn = id["identifier"]
    if isbn is None:
        continue
    logging.info(f"Found {isbn} for {ressource['title']}")
    cur.execute("UPDATE ressources SET isbn = ? WHERE slug = ? and video_id = ?",
                (isbn, ressource["slug"], ressource["video_id"]))
    con.commit()
