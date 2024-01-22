import json
from dotenv import load_dotenv
import sqlite3
import logging
from scripts.db import get_connection
import requests
import os

load_dotenv()
logging.basicConfig(level=logging.INFO)
con = get_connection()
cur = con.cursor()

for ressource in cur.execute("SELECT * FROM ressources WHERE kind='book' AND isbn IS NOT NULL AND google_books_json IS NOT NULL AND (authors IS NULL OR authors = '' OR book_title IS NULL OR book_title = '')").fetchall():
    data = json.loads(ressource["google_books_json"])
    authors = data["volumeInfo"].get("authors") or None
    authors_str = ", ".join(authors) if authors else None
    title = data["volumeInfo"].get("title") or None
    subtitle = data["volumeInfo"].get("subtitle") or None
    logging.info(
        f"updating {ressource['title']}  with title "
        f"{title}, subtitle {subtitle} and authors {authors_str}"
    )
    cur.execute(
        "UPDATE ressources SET authors = ?, book_title = ?, book_subtitle = ? WHERE isbn = ?",
        (
            authors_str,
            title,
            subtitle,
            ressource["isbn"]
        )
    )
    con.commit()
