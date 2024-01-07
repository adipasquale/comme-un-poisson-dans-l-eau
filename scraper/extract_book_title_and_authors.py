import json
from dotenv import load_dotenv
import sqlite3
import logging
from db import get_connection
import requests
import os

load_dotenv()
logging.basicConfig(level=logging.INFO)
con = get_connection()
cur = con.cursor()

try:
    cur.execute("ALTER TABLE ressources ADD COLUMN authors TEXT")
    cur.execute("ALTER TABLE ressources ADD COLUMN book_title TEXT")
    cur.execute("ALTER TABLE ressources ADD COLUMN book_subtitle TEXT")
except sqlite3.OperationalError:
    pass

for ressource in cur.execute("SELECT * FROM ressources WHERE kind='book' AND google_books_json IS NOT NULL AND (authors IS NULL OR book_title IS NULL)").fetchall():
    data = json.loads(ressource["google_books_json"])

    authors = data["volumeInfo"].get("authors") or None
    authors_str = ", ".join(authors) if authors else None
    title = data["volumeInfo"].get("title") or None
    subtitle = data["volumeInfo"].get("subtitle") or None
    logging.info(
        f"updating {ressource['slug']} #{ressource['video_id']} with title "
        f"{title}, subtitle {subtitle} and authors {authors_str}"
    )
    cur.execute(
        "UPDATE ressources SET authors = ?, book_title = ?, book_subtitle = ? WHERE slug = ? and video_id = ?",
        (
            authors_str,
            title,
            subtitle,
            ressource["slug"],
            ressource["video_id"]
        )
    )
    con.commit()
